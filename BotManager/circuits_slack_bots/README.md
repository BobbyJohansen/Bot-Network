This is a different way to utilize events on a bot and an integration in this case slack.
It uses circuits events.

I keeping both in here because I am not sure which one will be nicer to work with and without knowing
I do not want to build myself into a corner.


The premise here is that the bot should contain a slack listener and build out a slack event listener
the event listener is registered with the slack listener which goes like this:

| slack listener receives event from slack:
       |
       | - > event is mapped from string to Circuit.Event and fired using the producer
                |
                | - > The event is received by all registered listeners waiting for that event.
                        |
                        | - > The bot acts upon the event somehow need to send it back (implement an echo)