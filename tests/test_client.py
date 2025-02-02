import unittest
from unittest.mock import patch, MagicMock
from client import ChatClient
from utils import HEADER_LENGTH, generate_header

class TestChatClient(unittest.TestCase):
    def setUp(self):
        """Set up a ChatClient instance for testing."""
        self.client = ChatClient('127.0.0.1', 1234, 'User')
        self.addCleanup(self.client.client_socket.close) #ensures cleanup

    @patch('socket.socket')
    def test_connect(self, mock_socket):
        """Test connecting to the server."""
        mock_socket_instance = mock_socket.return_value
        self.client.client_socket = mock_socket_instance 

        self.client.connect()

        username = self.client.username
        username_header = generate_header(username)
        
        mock_socket_instance.connect.assert_called_once_with(('127.0.0.1', 1234))
        mock_socket_instance.setblocking.assert_called_once_with(False)
        mock_socket_instance.send.assert_called_once_with(username_header + username)

    @patch('socket.socket')
    def test_terminate(self, mock_socket):
        """Test terminating the client."""
        mock_socket_instance = mock_socket.return_value
        self.client.client_socket = mock_socket_instance

        self.client.terminate()

        self.assertTrue(self.client.termination_flag.is_set())
        mock_socket_instance.close.assert_called_once()

    @patch('socket.socket')
    def test_receive_messages(self, mock_socket):
        """Test receiving messages from the server."""
        mock_socket_instance = mock_socket.return_value
        self.client.client_socket = mock_socket_instance

        mock_socket_instance.recv.side_effect = [b'5', b'Hello']

        with patch('sys.stdout', new_callable=MagicMock):
            self.client.receive_messages()

        mock_socket_instance.recv.assert_called()

    @patch('socket.socket')
    @patch('builtins.input', side_effect=['Hello', '!logout'])
    def test_send_messages(self, mock_input, mock_socket):
        """Test sending messages to the server."""
        mock_socket_instance = mock_socket.return_value
        self.client.client_socket = mock_socket_instance

        self.client.send_messages()

        mock_socket_instance.send.assert_called()

if __name__ == '__main__':
    unittest.main()