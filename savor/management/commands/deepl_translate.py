
import os
import polib
import deepl
from django.conf import settings
from django.core.management.base import BaseCommand
from pathlib import Path

class Command(BaseCommand):
    help = 'Translate .po files using DeepL API'

    def add_arguments(self, parser):
        parser.add_argument(
            '-l', '--locale',
            action='append',
            help='Translate only the specified locale(s). Can be used multiple times.',
        )

    def handle(self, *args, **options):
        try:
            auth_key = settings.DEEPL_API_KEY
            translator = deepl.Translator(auth_key)
        except AttributeError:
            self.stderr.write(self.style.ERROR("DEEPL_API_KEY not found in settings.py"))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to initialize DeepL translator: {e}"))
            return
        
        requested_locales = options['locale']

        locale_paths = settings.LOCALE_PATHS
        for locale_path in locale_paths:
            for root, _, files in os.walk(locale_path):
                for file in files:
                    if file.endswith('.po'):
                        po_file_path = os.path.join(root, file)

                        current_locale = Path(po_file_path).parent.parent.name
                        if requested_locales and current_locale not in requested_locales:
                            continue

                        self.stdout.write(f'Processing file: {po_file_path}')
                        self.translate_po_file(translator, po_file_path)

        self.stdout.write(self.style.SUCCESS('Translation process finished.'))

    def translate_po_file(self, translator, file_path):
        try:
            po = polib.pofile(file_path)
            target_language_code = Path(file_path).parent.parent.name
            
            if len(target_language_code) > 2:
                 target_language_code = target_language_code.split('_')[0]
            target_language_code = target_language_code.upper()

            if target_language_code == 'PT':
                target_language_code = 'PT-PT'


            untranslated_entries = [e for e in po if (not e.msgstr or 'fuzzy' in e.flags) and e.msgid]

            if not untranslated_entries:
                self.stdout.write(f' -> No untranslated entries found. Skipping.')
                return

            self.stdout.write(f' -> Found {len(untranslated_entries)} untranslated entries for language "{target_language_code}"')
            
            for entry in untranslated_entries:
                try:
                    result = translator.translate_text(
                        entry.msgid, 
                        source_lang="EN", 
                        target_lang=target_language_code
                    )
                    entry.msgstr = result.text

                    if 'fuzzy' in entry.flags:
                        entry.flags.remove('fuzzy')
                        
                except deepl.DeepLException as e:
                    self.stderr.write(self.style.ERROR(f' -> Error translating "{entry.msgid}": {e}'))
                except Exception as e:
                     self.stderr.write(self.style.ERROR(f' -> An unexpected error occurred: {e}'))

            po.save(file_path)
            self.stdout.write(self.style.SUCCESS(f' -> Successfully saved translations to {file_path}'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Could not process file {file_path}: {e}'))