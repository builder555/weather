from unittest.mock import MagicMock, patch, Mock, call, ANY
from mqttpub import PublisherMQTT

class TestMQTTAdaptor:

    def test_publishing_sends_payload_under_specified_topic(self):
        fake_client = MagicMock()
        fake_mqtt = MagicMock(Client=lambda: fake_client)
        with patch('mqttpub.main.mqtt', new=fake_mqtt) as m:
            publisher = PublisherMQTT('hello1')
            publisher.publish('test2')
            fake_client.publish.assert_called_with(topic='hello1', payload='test2')

    def test_client_connects_publishes_disconnects_in_that_order(self):
        manager = MagicMock()
        fake_client = MagicMock(connect=Mock(),publish=Mock(),disconnect=Mock())
        fake_mqtt = MagicMock(Client=lambda: fake_client)
        manager.attach_mock(fake_client.connect,'connect')
        manager.attach_mock(fake_client.publish,'publish')
        manager.attach_mock(fake_client.disconnect,'disconnect')
        with patch('mqttpub.main.mqtt', new=fake_mqtt):
            publisher = PublisherMQTT('x')
            publisher.publish('y')
            expected_calls = [call.connect(ANY,ANY), call.publish(topic=ANY, payload=ANY), call.disconnect()]
            assert manager.mock_calls == expected_calls

