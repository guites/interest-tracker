#!/usr/bin/env python3

import argparse
import sqlite3
import sys

from datetime import datetime, timedelta


def parse_effort(time_string: str) -> int:
    """receives `time_string` in HH:MM:SS format and return
    the number of seconds as an integer.

    based on https://stackoverflow.com/a/12352624/14427854

    Raises:
        ValueError: time_string is incorrectly formatted

    Return: int (time in seconds)"""
    date_time = datetime.strptime(time_string, "%H:%M")
    time_delta = timedelta(hours=date_time.hour, minutes=date_time.minute)
    return int(time_delta.total_seconds())


def parse_tags(tags: str) -> "list[str]":
    """splits a list of tags by comma and replaces any internal spaces with underlines

    Return: list[str] (list of tags)"""
    if tags is not None:
        return [t.strip().replace(" ", "_") for t in tags.split(",")]
    return []


class SqliteHandler:
    def __init__(self):
        self.connection = sqlite3.connect("interest_tracker.db")
        self.cursor = self.connection.cursor()
        self.__create_tables()

    def __create_tables(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS interests(id INTEGER PRIMARY KEY, log TEXT, effort INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP);"
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS tags(id INTEGER PRIMARY KEY, name VARCHAR(255));"
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS interests_tags (interest_id INTEGER, tag_id INTEGER, FOREIGN KEY(interest_id) REFERENCES interest, FOREIGN KEY(tag_id) REFERENCES tag);"
        )

    def __create_tags(self, tags: "list[str]"):
        created_tag_ids = []
        for tag in tags:
            self.cursor.execute("""INSERT INTO tags (name) VALUES (?)""", (tag,))
            self.connection.commit()
            created_tag_ids.append(self.cursor.lastrowid)
        return created_tag_ids

    def __relate_tags_to_interest(self, interest_id: int, tag_ids: "list[int]"):
        data = [(interest_id, tag_id) for tag_id in tag_ids]
        self.cursor.executemany("INSERT INTO interests_tags VALUES(?, ?)", data)
        self.connection.commit()

    def __handle_tags(self, interest_id, tags: "list[str]"):
        bind_params = ", ".join(["?"] * len(tags))
        escaped_query = f"SELECT id, name FROM tags WHERE name IN ({bind_params})"
        query_result = self.cursor.execute(escaped_query, tags)
        existing_tags = query_result.fetchall()

        existing_tag_ids = []
        existing_tag_names = []
        for existing_tag_id, existing_tag_name in existing_tags:
            existing_tag_ids.append(existing_tag_id)
            existing_tag_names.append(existing_tag_name)

        tag_ids_to_relate = []
        tags_to_create = []
        for tag in tags:
            if tag in existing_tag_names:
                index_in_list = existing_tag_names.index(tag)
                tag_ids_to_relate.append(existing_tag_ids[index_in_list])
            else:
                tags_to_create.append(tag)

        self.__relate_tags_to_interest(
            interest_id, tag_ids_to_relate + self.__create_tags(tags_to_create)
        )

    def add_interest(self, log: str, effort: int, tags: "list[str]"):
        self.cursor.execute(
            """
            INSERT INTO interests (log, effort) VALUES (?, ?)
        """,
            (log, effort),
        )
        self.connection.commit()
        if tags is not None:
            interest_id = self.cursor.lastrowid
            self.__handle_tags(interest_id, tags)

    def show_interests(self):
        show_interests_query = """
            SELECT i.log, i.effort, GROUP_CONCAT(t.name, ',') FROM interests i INNER JOIN interests_tags it ON i.id = it.interest_id INNER JOIN tags t ON it.tag_id = t.id GROUP BY i.id;
        """
        for row in self.cursor.execute(show_interests_query):
            print(row)


class InterestTracker:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Track your hacking sessions with this simple cli app.",
            usage="""interest-tracker.py <command> [<args>]

Available commands are:
    log         Register a new hacking interest
    visualize   Visualize existing interests
""",
            epilog="a joint venture by guites <https://github.com/guites> and D3C0RU5 <https://github.com/D3C0RU5>.",
        )

        parser.add_argument("command", help="Subcommand to run")
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print("Unrecognized command")
            parser.print_usage()
            sys.exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def log(self):
        parser = argparse.ArgumentParser(description="Register a new hacking interest")
        parser.add_argument("log", metavar="LOG", help="What you've been hacking at")
        parser.add_argument(
            "-e", "--effort", required=True, help="How long you've been at it (HH:MM)"
        )
        parser.add_argument(
            "-t", "--tags", help="Comma separated tags to group your interests"
        )
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (interest-tracker) and the subcommand (log)
        args = parser.parse_args(sys.argv[2:])
        sql_handler = SqliteHandler()
        try:
            parsed_effort = parse_effort(args.effort)
        except ValueError:
            parser.error("EFFORT (-e, --effort) should be in HH:MM format")

        parsed_tags = parse_tags(args.tags)

        sql_handler.add_interest(log=args.log, effort=parsed_effort, tags=parsed_tags)

    def visualize(self):
        # TODO: should be able to filter by day, week, month, etc
        # parser = argparse.ArgumentParser(description="Visualize existing interests")
        # parser.add_argument("")
        sql_handler = SqliteHandler()
        sql_handler.show_interests()


if __name__ == "__main__":
    InterestTracker()
