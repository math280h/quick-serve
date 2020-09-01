# quick-serve
A very simple and limited HTTP Server

## Threading
quick-serve uses Threading to handle many requests, once a connection is accepted it's moved into it's own thread.

## Testing
`unittests` are located in src/tests and can be run by using the unittests python package.

Current Tests:
* get
    * test_undefined_word - Tests that we get the correct response by suplying an undefined word
    * test_invalid - Tests that we get the correct response when suplying an invalid `GET` command
* connection
    * test_welcome_message - Tests that we get the correct welcome message when connecting
    * test_connection - Tests that we can connect to the server