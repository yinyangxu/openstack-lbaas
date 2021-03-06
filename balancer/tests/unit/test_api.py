import unittest
import mock
import balancer.exception as exception

from balancer.api.v1 import loadbalancers
from balancer.api.v1 import devices


class TestLoadBalancersController(unittest.TestCase):
    def setUp(self):
        super(TestLoadBalancersController, self).setUp()
        self.conf = mock.Mock()
        self.controller = loadbalancers.Controller(self.conf)
        self.req = mock.Mock()

    @mock.patch('balancer.core.api.lb_find_for_vm', autospec=True)
    def test_find_lb_for_vm(self, mock_lb_find_for_vm):
        mock_lb_find_for_vm.return_value = 'foo'
        self.req.headers = {'X-Tenant-Id': 'fake_tenant_id',
                            'X-Tenant-Name': 'fake_tenant_name'}
        resp = self.controller.findLBforVM(self.req, vm_id='123')
        self.assertTrue(mock_lb_find_for_vm.called)
        self.assertEqual(resp, {'loadbalancers': 'foo'})

    @mock.patch('balancer.core.api.lb_get_index', autospec=True)
    def test_index(self, mock_lb_get_index):
        mock_lb_get_index.return_value = 'foo'
        self.req.headers = {'X-Tenant-Id': 'fake_tenant_id'}
        resp = self.controller.index(self.req)
        self.assertTrue(mock_lb_get_index.called)
        self.assertEqual(resp, {'loadbalancers': 'foo'})

    @mock.patch('balancer.core.api.create_lb', autospec=True)
    @mock.patch('balancer.db.api.loadbalancer_create', autospec=True)
    def test_create(self, mock_loadbalancer_create, mock_create_lb):
        mock_loadbalancer_create.return_value = {'id': '1'}
        mock_create_lb.return_value = {'id': '1'}
        self.req.headers = {'X-Tenant-Id': 'fake_tenant_id'}
        resp = self.controller.create(self.req, body={})
        self.assertTrue(mock_loadbalancer_create.called)
        self.assertTrue(mock_create_lb.called)
        self.assertEqual(resp, {'loadbalancers': {'id': '1'}})
        self.assertTrue(hasattr(self.controller.create, "wsgi_code"),
            "has not redifined HTTP status code")
        self.assertTrue(self.controller.create.wsgi_code == 202,
        "incorrect HTTP status code")

    @mock.patch('balancer.core.api.delete_lb', autospec=True)
    def test_delete(self, mock_delete_lb):
        resp = self.controller.delete(self.req, id='123')
        self.assertTrue(mock_delete_lb.called)
        self.assertTrue(hasattr(self.controller.delete, "wsgi_code"),
            "has not redifined HTTP status code")
        self.assertTrue(self.controller.delete.wsgi_code == 204,
            "incorrect HTTP status code")

    @mock.patch('balancer.core.api.lb_get_data', autospec=True)
    def test_show(self, mock_lb_get_data):
        mock_lb_get_data.return_value = 'foo'
        resp = self.controller.show(self.req, id='123')
        self.assertTrue(mock_lb_get_data.called)
        self.assertEqual(resp, {'loadbalancer': 'foo'})

    @mock.patch('balancer.core.api.lb_show_details', autospec=True)
    def test_show_details(self, mock_lb_show_details):
        mock_lb_show_details.return_value = 'foo'
        resp = self.controller.showDetails(self.req, id='123')
        self.assertTrue(mock_lb_show_details.called)
        self.assertEqual('foo', resp)

    @mock.patch('balancer.core.api.update_lb', autospec=True)
    def test_update(self, mock_update_lb):
        resp = self.controller.update(self.req, id='123', body='body')
        self.assertTrue(mock_update_lb.called)
        self.assertTrue(hasattr(self.controller.update, "wsgi_code"),
            "has not redifined HTTP status code")
        self.assertTrue(self.controller.update.wsgi_code == 202,
            "incorrect HTTP status code")

    @mock.patch('balancer.core.api.lb_add_nodes', autospec=True)
    def test_add_nodes(self, mock_lb_add_nodes):
        mock_lb_add_nodes.return_value = 'foo'
        resp = self.controller.addNodes(self.req, id='123',
                                                 body={'nodes': 'foo'})
        self.assertTrue(mock_lb_add_nodes.called)
        self.assertEqual(resp, 'foo')

    @mock.patch('balancer.core.api.lb_show_nodes', autospec=True)
    def test_show_nodes(self, mock_lb_show_nodes):
        mock_lb_show_nodes.return_value = 'foo'
        resp = self.controller.showNodes(self.req, id='123')
        self.assertTrue(mock_lb_show_nodes.called)
        self.assertEqual(resp, 'foo')

    @mock.patch("balancer.db.api.server_get")
    @mock.patch("balancer.db.api.unpack_extra")
    def test_show_node(self, mock_server_get, mock_unpack):
        mock_server_get.return_value = 'foo'
        resp = self.controller.showNode(self.req, '123', '123')
        self.assertTrue(mock_server_get.called)
        self.assertTrue(mock_unpack.called)
        self.assertEqual(resp, {'node': 'foo'})

    @mock.patch('balancer.core.api.lb_delete_node', autospec=True)
    def test_delete_node(self, mock_lb_delete_node):
        resp = self.controller.deleteNode(self.req, id='123', nodeID='321')
        self.assertTrue(mock_lb_delete_node.called)
        self.assertTrue(hasattr(self.controller.deleteNode, "wsgi_code"),
            "has not redifined HTTP status code")
        self.assertTrue(self.controller.deleteNode.wsgi_code == 204,
            "incorrect HTTP status code")

    @mock.patch('balancer.core.api.lb_change_node_status', autospec=True)
    def test_change_node_status(self, mock_lb_change_node_status):
        req_kwargs = {'id': '1',
                      'nodeID': '1',
                      'status': 'FAKESTATUSA'}
        resp = self.controller.changeNodeStatus(self.req, **req_kwargs)
        self.assertTrue(mock_lb_change_node_status.called)

    @mock.patch('balancer.core.api.lb_update_node', autospec=True)
    def test_update_node(self, mock_lb_update_node):
        req_kwargs = {'lb_id': '1',
                      'lb_node_id': '1',
                      'body': {'node': 'node'}}
        resp = self.controller.updateNode(self.req, **req_kwargs)
        self.assertTrue(mock_lb_update_node.called)

    @mock.patch('balancer.core.api.lb_show_probes', autospec=True)
    def test_show_monitoring(self, mock_lb_show_probes):
        mock_lb_show_probes.return_value = 'foo'
        resp = self.controller.showMonitoring(self.req, id='1')
        self.assertTrue(mock_lb_show_probes.called)
        self.assertEqual(resp, 'foo')

    @mock.patch('balancer.core.api.lb_add_probe', autospec=True)
    def test_add_probe(self, mock_lb_add_probe):
        mock_lb_add_probe.return_value = '1'
        req_kwargs = {'id': '1',
                      'body': {'healthMonitoring': {'probe': 'foo'}}}
        resp = self.controller.addProbe(self.req, **req_kwargs)
        self.assertTrue(mock_lb_add_probe.called)
        self.assertEqual(resp, 'probe: 1')

    @mock.patch('balancer.core.api.lb_delete_probe', autospec=True)
    def test_delete_probe(self, mock_lb_delete_probe):
        resp = self.controller.deleteProbe(self.req, id='1', probeID='1')
        self.assertTrue(mock_lb_delete_probe.called)
        self.assertTrue(hasattr(self.controller.deleteProbe, "wsgi_code"),
            "has not redifined HTTP status code")
        self.assertTrue(self.controller.deleteProbe.wsgi_code == 204,
            "incorrect HTTP status code")

    @mock.patch('balancer.core.api.lb_show_sticky', autospec=True)
    def test_show_stickiness(self, mock_lb_show_sticky):
        mock_lb_show_sticky.return_value = 'foo'
        resp = self.controller.showStickiness(self.req, id='1')
        self.assertTrue(mock_lb_show_sticky.called)
        self.assertEqual(resp, 'foo')

    @mock.patch('balancer.core.api.lb_add_sticky', autospec=True)
    def test_add_sticky(self, mock_lb_add_sticky):
        mock_lb_add_sticky.return_value = '1'
        req_kwargs = {'id': '1',
                      'body': {'sessionPersistence': 'foo'}}
        resp = self.controller.addSticky(self.req, **req_kwargs)
        self.assertTrue(mock_lb_add_sticky.called)
        self.assertEqual(resp, 'sticky: 1')

    @unittest.skip('incorrect response check')
    @mock.patch('balancer.core.api.lb_delete_sticky', autospec=True)
    def test_delete_sticky(self, mock_lb_delete_sticky):
        resp = self.controller.deleteSticky(self.req, id='1', stickyID='1')
        self.assertTrue(mock_lb_delete_sticky.called)
#        self.assertEqual(resp.status_int, 202)

    @mock.patch('balancer.db.api.unpack_extra', autospec=True)
    @mock.patch('balancer.db.api.virtualserver_get_all_by_lb_id',
                                                            autospec=True)
    def test_show_vips0(self, mock_get, mock_unpack):
        """VIPs should be found"""
        mock_get.return_value = ['foo']
        mock_unpack.return_value = 'foo1'
        resp = self.controller.showVIPs(self.req, '1')
        self.assertTrue(mock_get.called)
        self.assertTrue(mock_unpack.called)
        self.assertEqual(resp, {'vips': ['foo1']})

    @mock.patch('balancer.db.api.virtualserver_get_all_by_lb_id',
                                                           autospec=True)
    def test_show_vips1(self, mock_get):
        """Should raise exception"""
        mock_get.side_effect = exception.VirtualServerNotFound()
        with self.assertRaises(exception.VirtualServerNotFound):
            self.controller.showVIPs(self.req, '1')


class TestDeviceController(unittest.TestCase):
    def setUp(self):
        self.conf = mock.Mock()
        self.controller = devices.Controller(self.conf)
        self.req = mock.Mock()

    @mock.patch('balancer.core.api.device_get_index', autospec=True)
    def test_index(self, mock_device_get_index):
        mock_device_get_index.return_value = 'foo'
        resp = self.controller.index(self.req)
        self.assertTrue(mock_device_get_index.called)
        self.assertEqual({'devices': 'foo'}, resp)

    @mock.patch('balancer.core.api.device_create', autospec=True)
    def test_create(self, mock_device_create):
        mock_device_create.return_value = 'foo'
        resp = self.controller.create(self.req, body={})
        self.assertTrue(mock_device_create.called)
        self.assertEqual({'devices': 'foo'}, resp)

    @mock.patch('balancer.core.api.device_delete', autospec=True)
    def test_delete(self, mock_device_delete):
        resp = self.controller.delete(self.req, id='123')
        self.assertTrue(mock_device_delete.called)
        self.assertTrue(hasattr(self.controller.delete, "wsgi_code"),
                                "has not redifined HTTP status code")
        self.assertTrue(self.controller.delete.wsgi_code == 202,
        "incorrect HTTP status code")

    @unittest.skip('need to implement Controller.device_info')
    @mock.patch('balancer.core.api.device_info', autospec=True)
    def test_info(self, mock_device_info):
        mock_device_info.return_value = 'foo'
        resp = self.controller.device_info(self.req)
        self.assertTrue(mock_device_info.called)
        self.assertEqual({'devices': 'foo'}, resp)
