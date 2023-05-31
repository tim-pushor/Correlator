# Event system

The Correlator Event system consists of:

- Events: Python objects that contain data related to the event
- Event handlers: Instances of a Python class that catch dispatched Events and decide whether to either ignore the even 
or take action.

## Events

Events are dispatched from the front-end engine or one of its modules. They are modeled as python objects and
are instances of Correlator.event.Event or a subclass.

Standard event types are supplied to provide appropriate default actions. For example, any custom event
dispatched is a subclass of ErrorEvent will generate a python log entry with a severity of error when
being handled by the Logback listener.

## Standard events

The standard Event can contain quite a bit of information:

- Descriptive summary
- Data block - list of key/value pairs
- Timestamp
- The original log record (if applicable)
- System - source of the event
- optionally a text/html message generated bv mako
- Is this warning, error, or informational message

ErrorEvent, WarningEvent, and NoticeEvent are all subclasses of Event. To reiterate a point above, unless there is a
good reason not to, all non-audit type events should extend one of these standard event classes. 

## Audit events

Audit events are dispatched in response to something noteworthy happening, and have a defined data schema. This makes
these suitable to use as audit records as they can map easily to a CSV row, or database table.

All audit events are custom event classes that extend AuditEvent. An identifier and a list of data fields that will
be present in each event must be provided in the class defintion.

See Correlator.sshd.SSHDLoginEvent for an example.

## Event handlers

Event handlers are python objects that extend the Event.core.EventListener base class to take a custom action. When a 
Correlator module (or the Correlator system itself) dispatches an event, it forwards it to all registered event
handlers. Each handler must decide whether to take action based on the contents of the event.

There are several event handlers that ship with this distribution:

- logback:
    - writes events to the python log
- CSV:
    - Saves the data in audit events to rows in a CSV file
- Email:
    - Sends HTML or plaintext email via Mako templates driven from data within the event.
- SMS:
    - Twilio interface to send SMS messages with data from within the event