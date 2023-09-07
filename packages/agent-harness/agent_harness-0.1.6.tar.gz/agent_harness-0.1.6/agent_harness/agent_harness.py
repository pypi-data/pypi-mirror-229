"""
This is a file that has the following implemented.

# allows for the creation of a new user who wants to submit agents for benchmarking
register_user(username, password)

# allows for the creation of a new agent
register_agent(username, password, agent_name, code_path)

# allows for querying of benchmarks so users can easily choose what benchmarks they want to run
get_benchmark_ids(category=[], name=None, version='latest')

# starts the process of running a benchmark with the given id when this returns the agent can start working on the code
start_benchmark(id)

# allows the agent to ask a clarifying question before starting work on a ticket
ask_question(ticket_id, question)

# called when the agent is ready to submit the artifact. This will cause the code to be pushed to our git repo
submit_artifact(workspace: Path)
"""


from pathlib import Path
import time


import openapi_client
from openapi_client.apis.tags import default_api
from openapi_client.model.user import User
from openapi_client.model.create_user_request import CreateUserRequest
from openapi_client.model.errors_response import ErrorsResponse
from openapi_client import models
from pprint import pprint
from agent_harness.api_comms import (
    api_register_agent,
    handle_bids,
    upload_artifact,
    get_agents,
)


class PythonClientUser:
    def __init__(self, username: str, password: str, api_host: str):
        self.username = username
        self.password = password
        self.cfg = openapi_client.Configuration(
            host=api_host,
            username=self.username,
            password=self.password,
        )
        self.api = openapi_client.ApiClient(self.cfg)
        self.instance = default_api.DefaultApi(self.api)


def register_user(
    username: str,
    password: str,
    email: str,
    api_host: str = "https://marketplace-api.ai-maintainer.com/v1",
) -> PythonClientUser:
    """
    Allows for the creation of a new user who wants to submit agents for benchmarking.

    Args:
        username (str): The username of the user.
        password (str): The password for the user.

    Returns:
        None
    """
    # CLIENT_USERNAME = "test_user1"
    # CLIENT_PASSWORD = "F@k3awefawefawef"
    client = PythonClientUser(username, password, api_host)

    # create user. expect 201 or 409
    req = models.CreateUserRequest(userName=username, password=password, email=email)
    try:
        response = client.instance.create_user(req)
        assert response.response.status == 201
        return client
    except openapi_client.exceptions.ApiException as e:
        assert e.status == 409


def fetch_users_agents(client) -> list:
    """
    Fetches all agents for a given user.

    Args:
        username (str): The username of the user.
        password (str): The password for the user.

    Returns:
        list: A list of agents.
    """
    agents = get_agents(client)
    return agents


def register_agent(client, agent_name: str) -> str:
    """
    Allows for the creation of a new agent.

    Args:
        username (str): The username of the user.
        password (str): The password for the user.
        agent_name (str): The name of the agent being registered.
        code_path (str): The path to the agent's code.

    Returns:
        str: agent_id
    """
    agents = get_agents(client)
    for agent in agents:
        if agent["agentName"] == agent_name:
            if agent["userName"] == client.username:
                raise ValueError("User already has an agent with this name.")
            else:
                raise PermissionError(
                    f"Agent name {agent_name} is already taken by another user."
                )
    return api_register_agent(client, agent_name)


def get_benchmark_ids(
    client, category: list = [], name: str = None, version: str = "latest"
) -> list:
    """
    Allows for querying of benchmarks so users can easily choose what benchmarks they want to run.

    Args:
        category (list, optional): The category of benchmarks. Defaults to [].
        name (str, optional): The name of the benchmark. Defaults to None.
        version (str, optional): The version of the benchmark. Defaults to 'latest'.

    Returns:
        list: A list of benchmark IDs.
    """
    return ["c62e6410-2a95-4392-a21c-5f9a6a067230"]


def start_benchmark(client, id: int, code_path: Path, agent_id: str) -> None:
    """
    Starts the process of running a benchmark with the given id. When this returns, the agent can start working on the code.

    Args:
        id (int): The ID of the benchmark.
        code_path (Path): The path where code can be dumped into the workspace for the agent to start work.

    Returns:
        None
    """
    req = models.CreateBenchmarkTicketRequest(
        agentId=agent_id,
        benchmarkId=id,
    )
    response = client.instance.create_benchmark_ticket(req)
    while True:
        # poll for tickets assigned to this user
        response = client.instance.get_agent_tickets(
            query_params={
                "agentId": agent_id,
            }
        )
        tickets = list(response.body["tickets"])
        print("tickets:", tickets)
        if len(tickets) == 0:
            print("No tickets found. Sleeping.")
            time.sleep(2)
            continue
        ticket_id = tickets[0]["ticketId"]

        # create bid
        req = models.CreateBidRequest(
            agentId=agent_id,
            ticketId=ticket_id,
            rate=0.0,
        )
        response = client.instance.create_bid(req)
        print("response.body:", response.body)

        while True:
            # wait for the bids to be accepted.
            fork, bid_id, ticket = handle_bids(client, agent_id, code_path)
            print("fork:", fork)
            if fork:
                return fork, bid_id, ticket
            time.sleep(0.5)


def ask_question(ticket_id: int, question: str) -> None:
    """
    Allows the agent to ask a clarifying question before starting work on a ticket.

    Args:
        ticket_id (int): The ID of t    he ticket.
        question (str): The question being asked.

    Returns:
        None
    """
    return "No"


def submit_artifact(client, fork, bid_id: str, path: Path) -> None:
    """
    Called when the agent is ready to submit the artifact. This will cause the code to be pushed to our git repo.

    Args:
        workspace (Path): The path to the workspace containing the artifact.

    Returns:
        None
    """
    upload_artifact(client, fork, bid_id, path)
