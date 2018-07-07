# | Created by Ar4ikov
# | Время: 06.07.2018 - 21:44
import requests

from vk_advanced_api.data_proc import DataProcessing


class BotsLongPoll:

    def __init__(self, event_poll, utils, group_id) -> None:
        super().__init__()
        self.utils = utils
        self.group_id = group_id

        self.data_proc = DataProcessing(event_poll=event_poll, confirmation_key="")

    def __update_params(self):
        return self.utils.groups.getLongPollServer(group_id=self.group_id)

    def run(self):
        params = self.__update_params()
        while True:
            request = requests.post("{server}".format(
                server=params.get("server").replace("\\/", "/")
            ), params={
                "act": "a_check",
                "key": params.get("key"),
                "ts": params.get("ts"),
                "mode": 2,
                "version": 2,
                "wait": 25
            }).json()

            params["ts"] = request.get("ts")

            events = request.get("updates")

            if events is None:
                params = self.__update_params()
            else:
                for event in events:
                    self.data_proc.emit(event)


class UserLongPoll:
    def __init__(self, event_poll, utils, command_prefix, flags) -> None:
        super().__init__()

        self.event_poll = event_poll
        self.utils = utils
        self.command_prefix = command_prefix
        self.is_out = flags

    def __update_params(self):
        return self.utils.messages.getLongPollServer()

    def run(self):
        params = self.__update_params()
        while True:
            request = requests.post("https://{server}".format(
                server=params.get("server").replace("\\/", "/")
            ), params={
                "act": "a_check",
                "key": params.get("key"),
                "ts": params.get("ts"),
                "mode": 2,
                "version": 2,
                "wait": 25
            }).json()

            params["ts"] = request.get("ts")

            events = request.get("updates")

            if events is None:
                params = self.__update_params()
            else:
                messages = []
                for event in events:
                    if event[0] == 4:
                        messages.append(event)

                new_events = []
                for event in messages:
                    if event[-1].get('from'):
                        msg_type = 'public'
                        from_id = event[-1].get('from')
                    else:
                        msg_type = 'private'
                        from_id = event[3]

                    if event[-1].get('source_act'):
                        is_acted = True
                    else:
                        is_acted = False

                    act = event[-1].get('source_act')
                    act_mid = event[-1].get('source_mid')
                    act_text = event[-1].get('source_text')
                    act_from = event[-1].get('from')

                    attachments = []
                    attach_key = 'attach1'
                    attach_type = 'attach1_type'
                    for i in range(1, 11):
                        if event[-1].get(attach_key):
                            attachments.append(event[-1].get(attach_type) + event[-1].get(attach_key))
                            attach_key = attach_key[0:6] + str(i + 1)
                            attach_type = attach_key + "_type"
                        else:
                            break

                    args = event[5].replace("\\/", "/")
                    args = args.split(' ')

                    is_command = None
                    if len(''.join(args)) > 0:
                        if len(args) > 0:
                            if len(args[0]) > 0:
                                if args[0][0] == self.command_prefix:
                                    is_command = True
                                else:
                                    is_command = False

                    if self.is_out(event[2]):
                        is_out = True
                    else:
                        is_out = False

                    new_events.append(
                            dict(event='message_new', type=msg_type, text=event[5].replace("\\/", "/"), date=event[4], is_out=is_out, message_id=event[1],
                                 args=args, is_command=is_command, peer_id=event[3],
                                 from_id=from_id, body=event, is_acted=is_acted,
                                 acts=dict(act=act, act_mid=act_mid, act_text=act_text,
                                           act_from=act_from), attachments=attachments))

                for new in new_events:
                    if new['is_command']:
                        self.event_poll.emit('message_new', new, command=new['args'][0])
                    else:
                        self.event_poll.emit('message_new', new, command=None)
