import os
import runpy
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase


class ErrorReportingSettingsTest(SimpleTestCase):
    def load_settings(self, dsn):
        with (
            patch.dict(os.environ, {'SENTRY_DSN': dsn}),
            patch('dotenv.load_dotenv'),
            patch('sentry_sdk.init') as init,
        ):
            runpy.run_path(str(Path(__file__).with_name('settings.py')))
        return init

    def test_without_dsn_reporting_is_disabled(self):
        self.load_settings('').assert_not_called()

    def test_with_dsn_reporting_is_enabled_without_sensitive_data(self):
        init = self.load_settings('https://public@example.invalid/1')

        init.assert_called_once()
        options = init.call_args.kwargs
        self.assertEqual(options['dsn'], 'https://public@example.invalid/1')
        self.assertFalse(options['send_default_pii'])
        self.assertFalse(options['include_local_variables'])
        self.assertEqual(options['max_request_body_size'], 'never')
        self.assertEqual(options['traces_sample_rate'], 0)
        self.assertFalse(options['send_client_reports'])
        self.assertFalse(options['auto_session_tracking'])
        self.assertIn(
            'django', [item.identifier for item in options['integrations']]
        )
