# remoteconsole
Remote python console using HTTP.

## Description
It is not easy to have both GUI and console input. Some common problems are:

+ It's hard to running a main loop while accepting console input.
+ There will be output when editing the input line. It's very hard to keep the input line at the bottom of the console (though still can be done).
+ Even one manages to keep the console input line at the bottom, it's still somewhat inconvenient when there are a lot of output pouring out.
+ One can always write a dedicated UI for console input, though not very easy.

This python package contains a http server accepting console request, and a simple http client to send console commands and receive command output.

Working together they looks like a remote python console.

There are working code completion when the client has readline or prompt_toolkit. Note that enable greedy mode (the default) will cause more arbitrary code to be executed.

## Usage
Checkout the example with tkinter. Basically:

+ Integrate remoteconsole.server in your app, register code handler using set_request_handler, and call ConsoleServer.service periodically.
+ Run remoteconsole.client.
+ The server and client should agree on the ip address and port number.
+ Call ConsoleServer.shutdown when done.

You may want to copy the package sources to your app. It may be more convinent to directly modify the source.

You can customize code completion, modify remoteconsole/completion.py.

You can customize code handler, subclass remoteconsole.server.ConsoleRequestHandler, or directly modify PythonCodeHandler. For example, run GM commands if the line starts with % or $, not as raw python code.
