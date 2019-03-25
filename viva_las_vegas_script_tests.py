#!/usr/bin/env python3
# Copyright 2018 Anton Maksimovich <antonio.maksimovich@gmail.com>
# Copyright 2018 Simon Suprun <simonsuprun@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests related to the hubot-viva-las-vegas script. """

from argparse import ArgumentParser
from datetime import datetime, timedelta

from base import RocketChatTestCase

FROM_MSG = 'Ok, с какого числа? (дд.мм)'

INVALID_DATE_MSG = 'Указанная дата является невалидной. Попробуй еще раз.'

PERMISSION_DENIED_MSG = 'У тебя недостаточно прав для этой команды 🙄'

TO_MSG = 'Отлично, по какое? (дд.мм)'


class VivaLasVegasScriptTestCase(RocketChatTestCase):  # pylint: disable=too-many-instance-attributes
    """Tests for the hubot-viva-las-vegas script. """

    def __init__(self, addr, username, password, **kwargs):
        RocketChatTestCase.__init__(self, addr, username, password, **kwargs)

        self.schedule_pre_test_case('choose_general_channel')

        self.schedule_pre_test_case('_send_birthday_to_bot')

        self._bot_name = 'meeseeks'

        self._dividing_message = 'Hello from dividing message for tests'

        self._vacation_start_date = self._figure_out_date(15)

        self._too_close_start_date_1 = self._figure_out_date(1)

        self._too_close_start_date_2 = self._figure_out_date(2)

        self._vacation_end_date = self._figure_out_date(29)

        self._too_long_end_date = self._figure_out_date(44)

        self._max_response_date = self._figure_out_date(7)

        self._invalid_dates = ('99.99', '31.09', '30.02')

    #
    # Private methods
    #

    @staticmethod
    def _figure_out_date(days, date_format='%d.%m'):
        return (datetime.now() + timedelta(days=days)).strftime(date_format)

    def _send_birthday_to_bot(self):
        self.switch_channel(self._bot_name)
        self.send_message('01.01.1990')

    @staticmethod
    def _get_pre_weekends_dates():
        date = datetime.now() + timedelta(days=15)
        day = date.weekday()
        shift = 4 - day if day < 4 else 6 - day + 4
        start_date = date.strftime('%d.%m')
        end_date = (date + timedelta(days=shift)).strftime('%d.%m')

        return start_date, end_date, shift

    def _send_leave_request(self):
        self.send_message('{} хочу в отпуск'.format(self._bot_name))

        assert self.check_latest_response_with_retries(FROM_MSG)

        self.send_message('{} хочу в отпуск'.format(self._bot_name))

        assert self.check_latest_response_with_retries(
            'Давай по порядку!\n'
            'C какого числа ты хочешь уйти в отпуск? (дд.мм)')

    def _input_start_date(self):
        for date in self._invalid_dates:
            self.send_message('{0} {1}'.format(self._bot_name, date))

            assert self.check_latest_response_with_retries(INVALID_DATE_MSG)

        self.send_message('{0} {1}'.format(self._bot_name,
                                           self._too_close_start_date_1))

        assert self.check_latest_response_with_retries(
            'Нужно запрашивать отпуск минимум за 7 дней, а твой - уже завтра. '
            'Попробуй выбрать дату позднее {}.'.format(
                self._figure_out_date(7, '%d.%m.%Y')))

        self.send_message(
            '{0} {1}'.format(self._bot_name, self._too_close_start_date_2))

        assert self.check_latest_response_with_retries(
            'Нужно запрашивать отпуск минимум за 7 дней, '
            'а твой - только через 2 дня. '
            'Попробуй выбрать дату позднее {}.'.format(
                self._figure_out_date(7, '%d.%m.%Y')))

        self.send_message('{0} {1}'.format(self._bot_name,
                                           self._vacation_start_date))
        assert self.check_latest_response_with_retries(TO_MSG)

    def _input_end_date(self):
        for date in self._invalid_dates:
            self.send_message('{0} {1}'.format(self._bot_name, date))

            assert self.check_latest_response_with_retries(INVALID_DATE_MSG)

        self.send_message('{0} {1}'.format(self._bot_name,
                                           self._too_long_end_date))

        assert self.check_latest_response_with_retries(
            r'Отпуск продолжительностью \d* д(ня|ней|ень).*', match=True)

        self.send_message('{0} {1}'.format(self._bot_name,
                                           self._vacation_end_date))

        assert self.check_latest_response_with_retries(
            r'Значит ты планируешь находиться в отпуске \d* д(ня|ней|ень).*',
            match=True)

    def _confirm_dates(self, confirm=True):
        self.send_message('{0} {1}'.format(
            self._bot_name, 'Да, планирую' if confirm else 'Нет, не планирую'))

        assert self.check_latest_response_with_retries(
            'Заявка на отпуск отправлена. '
            'Ответ поступит не позже чем через 7 дней.'
            if confirm
            else 'Я прервал процесс формирования заявки на отпуск.')

    def _approve_request(self, username=None, is_admin=True):
        if not username:
            username = self.username
        self.send_message('{0} одобрить заявку @{1}'.format(self._bot_name,
                                                            username))
        if is_admin:

            assert self.check_latest_response_with_retries(
                "Заявка @{} одобрена. "
                "Я отправлю этому пользователю уведомление об этом.".format(username))

        else:

            assert self.check_latest_response_with_retries(
                PERMISSION_DENIED_MSG)

    def _reject_request(self, username=None, is_admin=True):
        if not username:
            username = self.username
        self.send_message('{0} отклонить заявку @{1}'.format(self._bot_name,
                                                             username))
        if is_admin:

            assert self.check_latest_response_with_retries(
                'Заявка @{} отклонена. '
                'Я отправлю этому пользователю уведомление об '
                'этом.'.format(username))
        else:

            assert self.check_latest_response_with_retries(
                PERMISSION_DENIED_MSG)

    def _cancel_approved_request(self, username=None, is_admin=True):
        if not username:
            username = self.username
        self.send_message('{0} отменить заявку @{1}'.format(self._bot_name,
                                                            username))
        if is_admin:

            assert self.check_latest_response_with_retries(
                "Отпуск пользователя @{} отменен.".format(username))
        else:

            assert self.check_latest_response_with_retries(
                PERMISSION_DENIED_MSG)

    def _send_dividing_message(self):
        self.send_message(self._dividing_message)

    def _check_approve_notification(self):

        assert self.get_message_by_number(-2).text == self._dividing_message

        assert self.check_latest_response_with_retries(
            'Заявка на отпуск одобрена.')

    def _check_reject_notification(self):

        assert self.get_message_by_number(-2).text == self._dividing_message

        assert self.check_latest_response_with_retries(
            'Заявка на отпуск отклонена.')

    def _check_cancel_notification(self):

        assert self.get_message_by_number(-2).text == self._dividing_message

        assert self.check_latest_response_with_retries(
            'Упс, пользователь @{0} '
            'только что отменил твою заявку на отпуск.'.format(self.username))

    def _check_vacation_notification(self):

        assert self.get_message_by_number(-2).text == self._dividing_message

        assert self.check_latest_response_with_retries(
            'Пользователь @{0} хочет в отпуск с .*'.format(self.username),
            match=True)

    def _check_approve_notification_in_channel(self):

        assert self.get_message_by_number(-2).text == self._dividing_message

        assert self.check_latest_response_with_retries(
            'Заявка на отпуск пользователя @{0} '
            'была одобрена пользователем @{0}.'.format(self.username))

    def _check_reject_notification_in_channel(self):

        assert self.get_message_by_number(-2).text == self._dividing_message

        assert self.check_latest_response_with_retries(
            'Заявка на отпуск пользователя @{0} '
            'была отклонена пользователем @{0}.'.format(self.username))

    def _check_cancel_notification_in_channel(self):

        assert self.get_message_by_number(-2).text == self._dividing_message

        assert self.check_latest_response_with_retries(
            'Пользователь @{0} отменил '
            'заявку на отпуск пользователя @{0}.'.format(self.username))

    #
    # Public methods
    #

    def test_sending_request_and_approving_it(self):
        """Tests if it's possible to send a leave request and approve it. """

        self.choose_general_channel()
        self._send_leave_request()
        self._input_start_date()
        self._input_end_date()
        self._confirm_dates()
        self._approve_request()
        self._cancel_approved_request()

    def test_sending_request_and_rejecting_it(self):
        """Tests if it's possible to send a leave request and reject it. """

        self._send_leave_request()
        self._input_start_date()
        self._input_end_date()
        self._confirm_dates()
        self._reject_request()

    def test_approve_notification(self):
        """Tests if it's possible to send a leave request, approve it and
        receive the corresponding message from the bot.
        """

        self.switch_channel(self._bot_name)
        self._send_dividing_message()
        self.choose_general_channel()
        self._send_leave_request()
        self._input_start_date()
        self._input_end_date()
        self._confirm_dates()
        self._approve_request()
        self.switch_channel(self._bot_name)
        self._check_approve_notification()
        self.choose_general_channel()
        self._cancel_approved_request()

    def test_reject_notification(self):
        """Tests if it's possible to send a leave request, reject it and
        receive the corresponding message from the bot.
        """

        self.switch_channel(self._bot_name)
        self._send_dividing_message()
        self.choose_general_channel()
        self._send_leave_request()
        self._input_start_date()
        self._input_end_date()
        self._confirm_dates()
        self._reject_request()
        self.switch_channel(self._bot_name)
        self._check_reject_notification()

    def test_cancel_notification(self):
        """Tests if it's possible to send a leave request, approve and cancel
        it, and receive the corresponding message from the bot.
        """

        self.choose_general_channel()
        self._send_leave_request()
        self._input_start_date()
        self._input_end_date()
        self._confirm_dates()
        self._approve_request()
        self.switch_channel(self._bot_name)
        self._send_dividing_message()
        self.choose_general_channel()
        self._cancel_approved_request()
        self.switch_channel(self._bot_name)
        self._check_cancel_notification()

    def test_for_adding_weekends_to_vacation(self):
        """Tests if the bot extends the length of the vacation period with
        weekends if the end of the period is on Friday.
        """

        self.send_message('{} хочу в отпуск'.format(self._bot_name))

        assert self.check_latest_response_with_retries(FROM_MSG)

        start_date, end_date, _ = self._get_pre_weekends_dates()
        self.send_message('{0} {1}'.format(self._bot_name, start_date))

        assert self.check_latest_response_with_retries(TO_MSG)

        self.send_message('{0} {1}'.format(self._bot_name, end_date))

        assert self.check_latest_response_with_retries(
            r'Значит ты планируешь находиться в отпуске \d* д(ня|ней|ень).*',
            match=True)

        self.send_message('{0} {1}'.format(self._bot_name, 'да'))

        self.send_message('{0} отклонить заявку @{1}'.format(self._bot_name,
                                                             self.username))

    def test_vacation_notification_in_channel(self):
        """Tests if the bot informs the users in the #leave-coordination
        channel when someone sends a leave request.
        """

        self.switch_channel('leave-coordination')
        self._send_dividing_message()
        self.choose_general_channel()
        self._send_leave_request()
        self._input_start_date()
        self._input_end_date()
        self._confirm_dates()
        self.switch_channel('leave-coordination')
        self._check_vacation_notification()
        self.choose_general_channel()
        self._approve_request()
        self._cancel_approved_request()

    def test_receiving_approval_in_channel(self):
        """Tests if the bot informs the users in the #leave-coordination
        channel when the admin approves a leave request.
        """

        self._send_leave_request()
        self._input_start_date()
        self._input_end_date()
        self._confirm_dates()
        self.switch_channel('leave-coordination')
        self._send_dividing_message()
        self.choose_general_channel()
        self._approve_request()
        self.switch_channel('leave-coordination')
        self._check_approve_notification_in_channel()
        self.choose_general_channel()
        self._cancel_approved_request()

    def test_receiving_reject_in_channel(self):
        """Tests if the bot informs the users in the #leave-coordination
        channel when the admin rejects a leave request.
        """

        self._send_leave_request()
        self._input_start_date()
        self._input_end_date()
        self._confirm_dates()
        self.switch_channel('leave-coordination')
        self._send_dividing_message()
        self.choose_general_channel()
        self._reject_request()
        self.switch_channel('leave-coordination')
        self._check_reject_notification_in_channel()

    def test_cancel_notification_in_channel(self):
        """Tests if the bot informs the users in the #leave-coordination
        channel when the admin cancels the approved leave request.
        """

        self.choose_general_channel()
        self._send_leave_request()
        self._input_start_date()
        self._input_end_date()
        self._confirm_dates()
        self._approve_request()
        self.switch_channel('leave-coordination')
        self._send_dividing_message()
        self.choose_general_channel()
        self._cancel_approved_request()
        self.switch_channel('leave-coordination')
        self._check_cancel_notification_in_channel()

    def test_sending_request_and_approving_it_without_permission(self):
        """Tests if it's not possible to approve a leave request without the
        corresponding permissions.
        """

        self.logout()
        self.login(use_test_user=True)
        self.choose_general_channel()

        self._send_leave_request()
        self._input_start_date()
        self._input_end_date()
        self._confirm_dates()
        self._approve_request(username=self.test_username, is_admin=False)

        self.logout()
        self.login()
        self.switch_channel('leave-coordination')
        self._approve_request(username=self.test_username)
        self._cancel_approved_request(username=self.test_username)

    def test_sending_request_and_rejecting_it_without_permission(self):
        """Tests if it's not possible to reject a leave request without the
        corresponding permissions.
        """

        self.logout()
        self.login(use_test_user=True)
        self.choose_general_channel()

        self._send_leave_request()
        self._input_start_date()
        self._input_end_date()
        self._confirm_dates()
        self._reject_request(username=self.test_username, is_admin=False)

        self.logout()
        self.login()
        self.switch_channel('leave-coordination')
        self._reject_request(username=self.test_username)


def main():
    """The main entry point. """

    parser = ArgumentParser(description='usage: %prog [options] arguments')
    parser.add_argument('-a', '--host', dest='host', type=str,
                        help='allows specifying admin username')
    parser.add_argument('-u', '--username', dest='username', type=str,
                        help='allows specifying admin username')
    parser.add_argument('-p', '--password', dest='password', type=str,
                        help='allows specifying admin password')
    options = parser.parse_args()

    if not options.host:
        parser.error('Host is not specified')

    if not options.username:
        parser.error('Username is not specified')

    if not options.password:
        parser.error('Password is not specified')

    test_cases = VivaLasVegasScriptTestCase(options.host, options.username,
                                            options.password,
                                            create_test_user=True)
    test_cases.run()


if __name__ == '__main__':
    main()
