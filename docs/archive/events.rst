cone.ugm.events
===============

You can react to creation, modification and deletion of users and groups
by binding to the given event classes.
These events are fired when the user manipulations are done in the UGM 
management forms.

necessary imports:
.. code-block:: python

    from zope.event import classhandler
    from cone.ugm import events

defining the event handlers
---------------------------

for users:

.. code-block:: python

    @classhandler.handler(events.UserCreatedEvent)
    def on_user_created(event):
        print(f"user {event.principal} with id {event.uid} created")


.. code-block:: python

    @classhandler.handler(events.UserModifiedEvent)
    def on_user_modified(event):
        print(f"user {event.principal} with id {event.uid} modified")


.. code-block:: python

    @classhandler.handler(events.UserDeletedEvent)
    def on_user_deleted(event):
        print(f"user {event.principal} with id {event.uid} deleted")

and for groups:

.. code-block:: python

    @classhandler.handler(events.GroupCreatedEvent)
    def on_group_created(event):
        print(f"group {event.principal} with id {event.uid} created")


.. code-block:: python

    @classhandler.handler(events.GroupModifiedEvent)
    def on_group_modified(event):
        print(f"group {event.principal} with id {event.uid} modified")


.. code-block:: python

    @classhandler.handler(events.GroupDeletedEvent)
    def on_group_deleted(event):
        print(f"group {event.principal} with id {event.uid} deleted")


