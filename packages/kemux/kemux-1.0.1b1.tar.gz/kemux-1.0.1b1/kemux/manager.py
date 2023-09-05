# pylint: disable=consider-using-enumerate
from __future__ import annotations

import asyncio
import dataclasses
import logging
import typing

import faust
import faust.types

import kemux.data.io.base
import kemux.data.io.input
import kemux.data.io.output
import kemux.data.schema.base
import kemux.data.schema.input
import kemux.data.schema.output
import kemux.data.stream

import kemux.logic.imports

DEFAULT_MODELS_PATH = 'streams'


@dataclasses.dataclass(kw_only=True)
class Manager:
    name: str
    kafka_address: str
    streams_dir: str | None
    persistent_data_directory: str
    logger: logging.Logger = dataclasses.field(init=False)
    agents: dict[str, faust.types.AgentT] = dataclasses.field(init=False, default_factory=dict)

    _app: faust.App = dataclasses.field(init=False)
    _event_loop: asyncio.AbstractEventLoop = dataclasses.field(init=False, default_factory=asyncio.get_event_loop)

    __instance: Manager | None = dataclasses.field(init=False, default=None)

    @property
    def streams(self) -> dict[str, kemux.data.stream.StreamBase]:
        return self.__streams

    @streams.setter
    def streams(self, streams: dict[str, kemux.data.stream.StreamBase]) -> None:
        self.__streams = kemux.data.stream.order_streams(streams)

    @classmethod
    def init(cls, name: str, kafka_address: str, data_dir: str, streams_dir: str | None = None) -> Manager:
        if cls.__instance is None:
            instance: Manager = cls(
                name=name,
                kafka_address=kafka_address,
                streams_dir=streams_dir,
                persistent_data_directory=data_dir,
            )
            instance.logger = faust.app.base.logger
            instance.logger.info('Initialized receiver')
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
            )
            instance.logger.info(f'Connecting to Kafka broker: {kafka_address}')
            app = faust.App(
                name,
                broker=kafka_address,
                value_serializer='json',
                datadir=instance.persistent_data_directory,
                stream_wait_empty=False,
                topic_allow_declare=False,
                topic_disable_leader=True,
                loop=instance._event_loop,
            )
            instance.streams = kemux.logic.imports.load_streams(streams_dir) if streams_dir else {}
            instance._app = app
            instance._app.logger = instance.logger
            cls.__instance = instance
        return cls.__instance

    def add_stream(self, name: str, stream_input_class: type, stream_outputs_class: type) -> None:
        stream_input = kemux.logic.imports.load_input(stream_input_class)
        stream_outputs = kemux.logic.imports.load_outputs(stream_outputs_class)
        self.streams = {
            **self.streams,
            name: kemux.data.stream.StreamBase(
                input=stream_input,
                outputs=stream_outputs,
            )
        }

    def remove_stream(self, name: str) -> None:
        if name not in self.streams:
            self.logger.warning(f'No stream found with name: {name}')
            return
        self.streams = {
            stream_name: stream
            for stream_name, stream in self.streams.items()
            if stream_name != name
        }

    def start(self) -> None:
        if not self.streams.keys():
            raise ValueError('No streams have been loaded!')

        self.logger.info('Initializing streams')
        self._event_loop.run_until_complete(
            self.initialize_streams()
        )

        self.logger.info('Starting receiver loop')
        self._app.main()

    async def initialize_streams(self) -> None:
        for stream_name, stream in self.streams.items():
            if (stream_input := stream.input) is None:
                raise ValueError(f'Invalid stream input: {stream_name}')
            self.logger.info(f'{stream_name}: activating input topic handler')

            stream_input.initialize_handler(self._app)
            input_topics_handler: faust.TopicT | None = stream_input.topic_handler
            if not input_topics_handler:
                raise ValueError(f'{stream_name}: invalid {stream_input.topic} input topic handler')

            output: kemux.data.io.output.StreamOutput
            for output in stream.outputs.values():
                output.initialize_handler(self._app)
                self.logger.info(f'{stream_name}: activating output topic handler: {output.topic}')
                await output.declare()

            self.logger.info(f'{stream_name}: activating stream agent')
            self.agents[stream_name] = self._app.agent(
                input_topics_handler
            )(
                self.create_processing_function(stream)
            )

    def create_processing_function(self, stream: kemux.data.stream.StreamBase) -> typing.Callable[[faust.StreamT[kemux.data.schema.input.InputSchema]], typing.Awaitable[None]]:
        async def _process_input_stream_message(events: faust.StreamT[kemux.data.schema.input.InputSchema]) -> None:
            event: faust.types.EventT
            async for event in events.events():
                await stream.process(event)
        _process_input_stream_message.__name__ = f'process_{stream.input.topic}_message'  # type: ignore
        _process_input_stream_message.__qualname__ = f'{self.__class__.__name__}.{_process_input_stream_message.__name__}'  # type: ignore
        return _process_input_stream_message
