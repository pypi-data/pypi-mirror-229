# SPDX-FileCopyrightText: 2020 Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

import amqpstorm  # type: ignore

from .cqrs import MiddlewareBase


def AmqpPublisherMiddleware(
    publisher_name: str, infrastructure_name: str = "amqp"
):
    """Return  `_AMQPPublisherClass` instantiated given params.

    :param publisher_name: name of publisher to get from config
    :type publisher_name: str
    :param infrastructure_name: name of amqp infrastructure, defaults to "amqp"
    :type infrastructure_name: str, optional
    :return: _AMQPPublisher middleware
    :rtype: _AMQPPublisher
    """

    class _AMQPPublisher(MiddlewareBase):
        """Publish all events in the event service to AMQP exchange."""

        def __call__(self, func):
            func()

            self.channel = self.infrastructure_factory.get_infrastructure(
                context=self.context, infrastructure_name=infrastructure_name
            )
            config = self.infrastructure_factory.get_config(
                context=self.context
            )
            publish_settings = config[infrastructure_name]["publish_settings"]
            exchange = publish_settings["exchange"]

            timer = self.statsd.get_timer("amqp_write_duration")
            counter = self.statsd.get_counter("amqp_write_number")

            for event in self.event_service.event_list:
                properties = {"content_type": "application/json"}

                event_content = event.as_json()
                routing_key = event.routing_key()

                message = amqpstorm.Message.create(
                    channel=self.channel,
                    body=event_content,
                    properties=properties,
                )

                self.logger.debug(
                    f"Publishing event {event.uuid} on {routing_key} - "
                    + str(message.method)
                    + " - "
                    + str(message.properties)
                    + " - EXCHANGE: "
                    + exchange
                )

                with timer.time():
                    message.publish(routing_key=routing_key, exchange=exchange)

                counter.increment()

    return _AMQPPublisher
