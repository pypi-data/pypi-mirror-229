"""
Module to implement a custom connection class for Cohost accounts,
supporting reading and writing messages from any of the user's projects.

Please read https://github.com/valknight/Cohost.py#readme for more information
regarding authenticating with cookies and / or user and password combinations.
"""

import logging
from typing import Optional

from cohost.models.user import User
from cohost.models.post import Post

from barkr.connections.base import Connection, ConnectionMode

logger = logging.getLogger()

class CohostConnection(Connection):
    """
    Custom connection class for Cohost accounts,
    supporting reading and writing messages from any of the user's projects.
    """

    def __init__(self, name: str, modes: list[ConnectionMode], project: str, cookie: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None)
        """
        Initializes the connection with a name and a list of modes,
        as well as setting up access to the user's account.

        Validates the user's credentials by connecting to Cohost and verifying that
        the provided project exists.

        Attempts to connect by cookie first, then by user and password combination
        if cookie is not provided.

        :param name: The name of the connection
        :param modes: A list of modes for the connection
        :param project: The name of the project to connect to
        :param cookie: The cookie for the authenticated user
        :param user: The username of the authenticated user
        :param password: The password of the authenticated user
        """

        super().__init__(name, modes)

        if user is not None and password is None:
            raise ValueError("User provided but no password provided, please set `password`.")

        logger.debug(
            "Initializing Cohost (%s) connection to project %s",
            self.name,
            project,
        )

        if cookie is not None:
            user: User = User.loginWithCookie(cookie)
        elif user is not None and password is not None:
            user = User.login(user, password)
        else:
            raise ValueError("No authentication method provided, please set either `cookie` OR `user` and `password`.")

        if project.startswith("@"):
            project = project[1:]

        if project not in user.editedProjects:
            raise ValueError("Project does not exist or is not writtable, please check your spelling and try again.")

        self.project = user.getProject(project)

        logger.info(
            "Cohost (%s) connection initialized! (Project name: %s)",
            self.name,
            self.project.displayName,
        )

        posts: list[Post] = self.project.getPosts()

        if posts:
            self.min_id = posts[0].postId
            logger.debug("Cohost (%s) initial min_id: %s", self.name, self.min_id)
        else:
            self.min_id = ""
            logger.debug("Cohost (%s) initial min_id not set.", self.name)


    def _post(self, messages: list[str]) -> None:
        """
        Post messages from a list to this Cohost project
        """

        for message in messages:
            self.project.post(message)
            logger.info("Cohost (%s) posted message: %s", self.name, message)
