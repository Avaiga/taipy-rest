from unittest import mock

from flask import url_for


def test_get_datanode(client, default_datanode):
    # test 404
    user_url = url_for("api.datanode_by_id", datanode_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.data.data_manager.DataManager.get") as manager_mock:
        manager_mock.return_value = default_datanode
        # test get_datanode
        rep = client.get(url_for("api.datanode_by_id", datanode_id="foo"))
        assert rep.status_code == 200


def test_delete_datanode(client):
    # test 404
    user_url = url_for("api.datanode_by_id", datanode_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.data.data_manager.DataManager.delete"):
        # test get_datanode
        rep = client.delete(url_for("api.datanode_by_id", datanode_id="foo"))
        assert rep.status_code == 200


def test_create_datanode(client, default_datanode_config):
    # without config param
    datanodes_url = url_for("api.datanodes")
    rep = client.post(datanodes_url)
    assert rep.status_code == 400

    # config does not exist
    datanodes_url = url_for("api.datanodes", config_name="foo")
    rep = client.post(datanodes_url)
    assert rep.status_code == 404

    with mock.patch(
        "taipy.rest.api.resources.datanode.DataNodeList.fetch_config"
    ) as config_mock:
        config_mock.return_value = default_datanode_config
        datanodes_url = url_for("api.datanodes", config_name="bar")
        rep = client.post(datanodes_url)
        assert rep.status_code == 201


def test_get_all_datanodes(client, default_datanode_config_list):
    for ds in range(10):
        with mock.patch(
            "src.taipy.rest.api.resources.datanode.DataNodeList.fetch_config"
        ) as config_mock:
            config_mock.return_value = default_datanode_config_list[ds]
            datanodes_url = url_for("api.datanodes", config_name=config_mock.name)
            client.post(datanodes_url)

    rep = client.get(datanodes_url)
    assert rep.status_code == 200

    results = rep.get_json()
    assert len(results) == 10


def test_read_datanode(client, default_df_datanode):
    with mock.patch("taipy.core.data.data_manager.DataManager.get") as config_mock:
        config_mock.side_effect = [default_df_datanode]
        # without operators
        datanodes_url = url_for("api.datanode_reader", datanode_id="foo")
        rep = client.get(datanodes_url)
        assert rep.status_code == 200

        # TODO: Revisit filter test
        # operators = {"operators": [{"key": "a", "value": 5, "operator": "LESS_THAN"}]}
        # rep = client.get(datanodes_url, json=operators)
        # assert rep.status_code == 200


def test_write_datanode(client, default_datanode):
    with mock.patch("taipy.core.data.data_manager.DataManager.get") as config_mock:
        config_mock.return_value = default_datanode
        # Get DataNode
        datanodes_read_url = url_for(
            "api.datanode_reader", datanode_id=default_datanode.id
        )
        rep = client.get(datanodes_read_url)
        assert rep.status_code == 200
        assert rep.json == {"data": [1, 2, 3, 4, 5, 6]}

        datanodes_write_url = url_for(
            "api.datanode_writer", datanode_id=default_datanode.id
        )
        rep = client.put(datanodes_write_url, json=[1, 2, 3])
        assert rep.status_code == 200

        rep = client.get(datanodes_read_url)
        assert rep.status_code == 200
        assert rep.json == {"data": [1, 2, 3]}
