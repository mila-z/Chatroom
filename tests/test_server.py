import unittest
import socket
from unittest.mock import patch, MagicMock
from server import ChatServer
from utils import generate_header, HEADER_LENGTH

class TestChatServer(unittest.TestCase):
    def setUp(self):
        """Set up a ChatServer instance for testing."""
        self.server = ChatServer('127.0.0.1', 1234)
        self.addCleanup(self.server.server_socket.close) #ensures cleanup

    @patch('socket.socket')
    def test_setup_server(self, mock_socket):
        """Test server setup."""
        self.server._setup_server()
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        self.server.server_socket.setsockopt.assert_called_once_with(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.server_socket.bind.assert_called_once_with(('127.0.0.1', 1234))
        self.server.server_socket.listen.assert_called_once()

    @patch('socket.socket')
    def test_receive_message(self, mock_socket):
        """Test receiving a message."""
        mock_client_socket = MagicMock()
        mock_client_socket.recv.side_effect = [
            b'10', # Header
            b'HelloWorld'
        ]
        result = self.server.receive_message(mock_client_socket)
        self.assertEqual(result, {'header': b'10', 'data': b'HelloWorld'})

    @patch('socket.socket')
    def test_send_message_to_all_except_sender(self, mock_socket):
        """Test sending a message to everyone except the sender."""
        mock_sender_socket = MagicMock()
        mock_client_socket = MagicMock()
        self.server.clients = {mock_client_socket: {}}
        self.server.send_message_to_all_except_sender(mock_sender_socket, b'Hello')
        # verify that send was called for the socket in the socket list
        mock_client_socket.send.assert_called_once_with(b'Hello')
        # verify that send was not called for the sender socket
        mock_sender_socket.send.assert_not_called()
    
    @patch('socket.socket')
    def test_handle_new_connection(self, mock_socket):
        """Test handlling a new connection."""
        mock_client_socket = MagicMock()
        mock_client_addr = ('127.0.0.1', 1234)
        user = {'header':b'10', 'data':b'User'}
        self.server.handle_new_connection(mock_client_socket, mock_client_addr, user)
        # verify that it was added to the lists
        self.assertIn(mock_client_socket, self.server.sockets_list)
        self.assertIn(mock_client_socket, self.server.clients)

    @patch('socket.socket')
    def test_handle_disconnection(self, mock_socket):
        """Test handling a disconnection."""
        mock_disconnected_socket = MagicMock()
        self.server.clients = {mock_disconnected_socket: {'data': b'User'}}
        self.server.sockets_list = [mock_disconnected_socket]
        self.server.handle_disconnection(mock_disconnected_socket)
        # verify that it was removed from the lists
        self.assertNotIn(mock_disconnected_socket, self.server.sockets_list)
        self.assertNotIn(mock_disconnected_socket, self.server.clients)

    @patch('socket.socket')
    def test_show_active_users_only_sender_active(self, mock_socket):
        """Test showing active users but no one else is active."""
        mock_sender_socket = MagicMock()
        self.server.clients = {mock_sender_socket: b'User'}
        expected_message = 'No one but you is active'.encode('utf-8')
        expected_message_header = generate_header(expected_message)
        self.server.show_active_users(mock_sender_socket)
        mock_sender_socket.send.assert_called_once_with(expected_message_header + expected_message)

    @patch('socket.socket')
    def test_show_active_users(self, mock_socket):
        """Test showing active users with other memebers active active."""
        mock_sender_socket = MagicMock()
        mock_client_socket = MagicMock()
        self.server.clients = {mock_client_socket: {'data': b'User'}}
        expected_message = '-> User'.encode('utf-8')
        expected_message_header = generate_header(expected_message)
        self.server.show_active_users(mock_sender_socket)
        mock_sender_socket.send.assert_called_once_with(expected_message_header + expected_message)

    @patch('socket.socket')
    def test_send_private_message_user_not_active(self, mock_socket):
        """Test sending a private message when the user is not active."""
        mock_sender_socket = MagicMock()
        self.server.clients = {
            mock_sender_socket: {'data': b'User1'},
        }
        self.server.send_private_message('User1', 'User2', 'Hello')
        expected_message = 'User2 is not online'.encode('utf-8')
        expected_message_header = generate_header(expected_message)
        mock_sender_socket.send.assert_called_once_with(expected_message_header + expected_message)

    @patch('socket.socket')
    def test_send_private_message_user_active(self, mock_socket):
        """Test sending a private message when the user is active."""
        mock_sender_socket = MagicMock()
        mock_receiver_socket = MagicMock()
        self.server.clients = {
            mock_sender_socket: {'data': b'User1'},
            mock_receiver_socket: {'data': b'User2'}
        }
        self.server.send_private_message('User1', 'User2', 'Hello')
        expected_message = 'privately User1 > Hello'.encode('utf-8')
        expected_message_header = generate_header(expected_message)
        mock_receiver_socket.send.assert_called_once_with(expected_message_header + expected_message)

    @patch('socket.socket')
    def test_broadcast_message_to_users_regular_message(self, mock_socket):
        """Test broadcasting a regular message to everyone."""
        mock_sender_socket = MagicMock()
        mock_receiver_socket = MagicMock()
        self.server.clients = {
            mock_sender_socket: {'data': b'User1'},
            mock_receiver_socket: {'data': b'User2'}
        }
        message = {'header': b'5', 'data': b'Hello'}
        expected_message = 'User1 > Hello'.encode('utf-8')
        expected_message_header = generate_header(expected_message)
        self.server.broadcast_message_to_users(mock_sender_socket, message)
        mock_receiver_socket.send.assert_called_once_with(expected_message_header + expected_message)
        mock_sender_socket.send.assert_not_called()

    @patch('socket.socket')
    def test_broadcast_message_to_users_who_command(self, mock_socket):
        """Test broadcasting a message that contains the who command for seeing the active users."""
        mock_sender_socket = MagicMock()
        mock_receiver_socket = MagicMock()
        self.server.clients = {
            mock_sender_socket: {'data': b'User1'},
            mock_receiver_socket: {'data': b'User2'}
        }
        message = {'header': b'4', 'data': b'!who'}
        with patch.object(self.server, 'show_active_users') as mock_show_active_users:
            self.server.broadcast_message_to_users(mock_sender_socket, message)
            mock_show_active_users.assert_called_once_with(mock_sender_socket)

    @patch('socket.socket')
    def test_broadcast_message_to_users_regular_msg_command(self, mock_socket):
        """Test broadcasting a message that contains the msg command for a private message."""
        mock_sender_socket = MagicMock()
        mock_receiver_socket = MagicMock()
        self.server.clients = {
            mock_sender_socket: {'data': b'User1'},
            mock_receiver_socket: {'data': b'User2'}
        }
        message = {'header':b'15', 'data': b'!msg User2 Hello'}
        with patch.object(self.server, 'send_private_message') as mock_send_private_message:
            self.server.broadcast_message_to_users(mock_sender_socket, message)
            mock_send_private_message.assert_called_once_with('User1', 'User2', 'Hello')

    @patch('socket.socket')
    def test_broadcast_message_to_users_no_active_users(self, mock_socket):
        """Test broadcasting a message to everyone."""
        mock_sender_socket = MagicMock()
        self.server.clients = {
            mock_sender_socket: {'data': b'User1'}
        }
        message = {'header': b'5', 'data': b'Hello'}
        self.server.broadcast_message_to_users(mock_sender_socket, message)
        mock_sender_socket.send.assert_not_called()

    
if __name__ == '__main__':
    unittest.main()