from itertools import cycle
from os.path import expanduser
import emoji
import hexchat


__module_name__ = "emojifier"
__module_version__ = "0.1"
__module_description__ = "Translate the text with colons into emojis"


print("Loading emojifier")
EMOJI_VALUES = list(emoji.UNICODE_EMOJI.values())
EMOJI_VALUES.extend(list(emoji.UNICODE_EMOJI_ALIAS.values()))

# See if there's a skin tone preference
try:
    with open(expanduser("~/.config/hexchat/emojifier_skin_tone")) as r:
        skin_preference = r.read().strip()
        # Find all the emojis that have that skin preference,
        # calculate their "roots", and remove the basic, yellow
        # versions.
        full_skin_suffix = "_{}_skin_tone".format(skin_preference)
        emojis_to_remove = [
            emoji.replace(full_skin_suffix, "")
            for emoji in EMOJI_VALUES
            if full_skin_suffix in emoji
        ]
        EMOJI_VALUES = [
            emoji
            for emoji in EMOJI_VALUES
            if full_skin_suffix in emoji or (
                    "skin_tone" not in emoji and
                    emoji not in emojis_to_remove
            )
        ]
except FileNotFoundError:
    pass


EMOJI_VALUES = sorted(set(EMOJI_VALUES))
emoji_autocompletion = []
last_msg = []


def autocomplete(avoid_infinite_loop=False):
    msg = hexchat.get_info('inputbox')
    if msg is None:
        return hexchat.EAT_NONE

    global emoji_autocompletion, last_msg
    if emoji_autocompletion:
        suggestion = next(emoji_autocompletion)
        replaced = ':'.join(last_msg[:-1]) + suggestion
        hexchat.command("settext %s" % replaced)
        hexchat.command("setcursor %s" % len(replaced))
        return hexchat.EAT_ALL
    last_msg = msg.split(':')
    if len(last_msg) == 1 or not last_msg[-1]:
        return
    emoji_search = ':' + last_msg[-1]
    emoji_autocompletion = []
    for v in EMOJI_VALUES:
        if v.startswith(emoji_search):
            emoji_autocompletion.append(v)
    if not avoid_infinite_loop:
        if len(emoji_autocompletion) > 1:
            print([
                "%s (%s)" % (e, emoji.emojize(e, use_aliases=True))
                for e in emoji_autocompletion
            ])
        if emoji_autocompletion:
            emoji_autocompletion = cycle(emoji_autocompletion)
        return autocomplete(True)


def send_message(word, word_eol, userdata):
    if (word[0] == "65289"):
        return autocomplete()
    global emoji_autocompletion, last_msg
    emoji_autocompletion = []
    last_msg = []
    if not(word[0] == "65293"):
        return hexchat.EAT_NONE
    msg = hexchat.get_info('inputbox')
    if msg is None:
        return hexchat.EAT_NONE

    replaced = emoji.emojize(msg, use_aliases=True)
    if replaced != msg:
        hexchat.command("settext %s" % replaced)


hexchat.hook_print('Key Press', send_message)
