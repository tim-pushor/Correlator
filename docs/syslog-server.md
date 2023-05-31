# The syslog server front end

The syslog server front end is responsible for listening on the network for syslog messages and forwarding them
through the stack for processing. It is implemented as a python class that is usable from client code, such as the
syslog_server CLI that is provided with this distribution.

## Network and application protocol

The syslog server implements RFC 6587 - Syslog over TCP. The parser expects syslog messages to be compliant with
RFC 5424 - The Syslog Protocol. The server has interoperated with limited number of syslog senders:

- a linux host running rsyslog with a forwarding rule to the address and port of the Correlator system.
- a proprietary software suite with an optional syslog logging interface.

## Syslog trailer discovery

RFC 6587 defines two methods of framing syslog messages.

*Section 3.4.1 Octet counting* describes a method in which the message length gets sent as part of the message.
*Section 3.4.2 Non-transparent-Framing* describes another method where the messages are separated by a record
seperator (the TRAILER).

Since the software I was using to drive development often generated multiline messages and used the second framing
method, the trailer is important. The default trailer of \n matches the newlines in the message and makes a mess of
things. 

This lead to the development of the feature called trailer discovery. When the system receives the first syslog message
from a new connection, it performs *trailer discovery* by calling the user defined function that was passed as an
argument when instantiating the server, if it exists.

This function's purpose is to use the data within the header to try to determine what the trailer should be, and return
it. If this function was either not provided to the syslog server class, or it it was and it raised an exception during
its execution, the value of the configuration item *syslog_server.default_trailer* is used.

## Packet capture and replay

The syslog server has the ability to write captured syslog packets to a file, and use the contents of these capture
files rather than listen on the network for syslog packets. The CLI utility caputil, represented by the file 
caputil.py uses this functionality. 

Although this is a tremendous help in developing module logic, it doesn't truly represent a syslog stream. Packets
don't arrive all at once. This also doesnt trigger the modules *timer handler* methods, so this feature is limited
in what it can test.

there is rudimentary filter that is meant to be used in the case where the input and output is both to a file. In this
case, when a filter is employed, the syslog server will read from one capture file, and only write packets into the
output file that are not filtered. This allows pruning unwanted records from capture files. Check caputil.py for
more details.

## Configuration parameters

The following configuration parameters affect the behavior of the syslog server:

| Key | Description | Type | Default value |
|-----|-------------|------|---------------|
| syslog_server.save_store_interval | Time in minutes in between saves of the persistence store | Integer | 5 |
| syslog_server.buffer_size | Read buffer size. This must be large enough so that an entire header including structured data can fit. | Integer | 4096 |
| syslog_server.default_trailer | The default syslog record separator to use if trailer discovery can't conclusively determine the record separator in use | String | '\n' |
| syslog_server.listen_address | The IPv4 address of the interface to listen on. 0.0.0.0 means listen on all interfaces. | String | '0.0.0.0' |
| syslog_server.listen_port | The TCP port number to listen on. | Integer | 514 |