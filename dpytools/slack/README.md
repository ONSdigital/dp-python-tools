# dpytools: Slack

## Usage

### SlackMessenger

The `SlackMessenger` class facilitates the creation of a client to send messages to a Slack channel, to notify users about important information relating to your application. To create a `SlackMessenger` object, you will need a [webhook URL](https://api.slack.com/messaging/webhooks). **This URL should be kept secret.** In the example below, the webhook URL has been set using a `WEBHOOK_URL` environment variable:

```python
import os
from dpytools.slack.slack import SlackMessenger

webhook_url = os.environ.get("WEBHOOK_URL")

slack_messenger = SlackMessenger(webhook_url=webhook_url)
```

### Methods

#### `msg()`

The `msg()` method sends a message to the Slack channel associated with the webhook URL that you set when creating the `SlackMessenger` object. This method accepts a `msg_dict` argument, which should be a dictionary that matches the [structure required by Slack](https://api.slack.com/reference/block-kit/composition-objects) to process and display messages.

```python
import os
from dpytools.slack.slack import SlackMessenger

webhook_url = os.environ.get("WEBHOOK_URL")

slack_messenger = SlackMessenger(webhook_url=webhook_url)

message = {
    "text": "This is a message"
}

slack_messenger.msg(msg_dict=message)
```

This will send the plain text message "This is a message" to the relevant Slack channel. It is also possible to format messages using markdown by specifying a `type` of `mrkdwn`:

```python
import os
from dpytools.slack.slack import SlackMessenger

webhook_url = os.environ.get("WEBHOOK_URL")

slack_messenger = SlackMessenger(webhook_url=webhook_url)

message = {
    "type": "mrkdwn",
    "text": "This is a message with a <http://www.example.org|link>"
}

slack_messenger.msg(msg_dict=message)
```

For more information on the formatting options available, see [Formatting text for app surfaces](https://api.slack.com/reference/surfaces/formatting).

#### `msg_str()`

The `msg_str()` method allows you to send a simple unformatted message string, without having to create a dictionary.

```python
import os
from dpytools.slack.slack import SlackMessenger

webhook_url = os.environ.get("WEBHOOK_URL")

slack_messenger = SlackMessenger(webhook_url=webhook_url)

slack_messenger.msg(msg="This is a message")
```

This will send the plain text message "This is a message" to the relevant Slack channel.