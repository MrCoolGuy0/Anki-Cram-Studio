"""Deterministic allowlisted release packaging; excludes all runtime/user data."""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED,ZipFile,ZipInfo

ROOT=Path(__file__).resolve().parent
FILES=['ai.py','gemini_transport.py','network_jobs.py','web/entry.js','writing.py','web/writing.js','web/writing.css','__init__.py','content.py','dialog.py','field_render.py','gemini.py','storage.py','session.py','ordering.py','live_review.py','live_start.py','appearance.py','appearance_images.py','customize.py','bulk_choices.py','deck_choices.py','manifest.json','README.md','web/app.html','web/app.css','web/app.js','web/live.js','web/live.css','web/live-bottom.css','web/appearance.js','web/appearance.css','web/customize.html','web/customize.js','web/customize.css','web/customize-preview.js']
DOCS=['WRITING-PROVIDER-FIX.md','tests/test_writing_provider_parity.py','tests/test_writing_provider_parity_qt.py','CHOICE-FORMAT-FIX.md','QUALITY-HOVER-FIX.md','tests/test_choice_quality.py','CLOZE-SPACE-FIX.md','tests/test_mcq_space_qt.py','tests/test_choice_stability.py','tests/test_choice_stability_qt.py','CHOICE-STABILITY.md','tests/test_grok_provider.py','DELIVERY-REQUIREMENTS.md','PROVIDERS.md','tests/test_ai_providers.py','tests/test_ai_settings_qt.py','tests/test_parallel_generation.py','tests/test_generation_speed.py','tests/test_network_jobs.py','tests/test_background_jobs.py','ADDON-PERFORMANCE-AUDIT.md','tests/test_home_catalog.py','tests/test_image_answers.py','tests/test_overview_pair_qt.py','tests/test_main_parity.py','tests/test_main_parity_qt.py','tests/test_flash_space.py','tests/test_mode_transitions.py','tests/test_flashcard_pointer.py','tests/test_mcq_blank_layout.py','tests/test_writing_scroll.py','tests/test_writing_layout.py','tests/test_writing.py','README.md','START-HERE.md','SCHEDULING-AUDIT.md','build.py','tests/test_core.py','tests/test_startup.py','tests/test_filters_session.py','tests/test_progress.py','tests/test_schedule_boundary.py','tests/test_ui.cjs','tests/test_v120.py','tests/test_live_review.py','tests/test_ordering.py','tests/test_appearance.py','tests/test_choices_update.py','tests/test_deck_choices.py']

def archive(path,entries):
    temporary=path.with_name(path.name+'.tmp')
    try:
        with ZipFile(temporary,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
            for name,data in sorted(entries.items()):
                info=ZipInfo(name,date_time=(2026,10,24,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o100644<<16
                z.writestr(info,data)
        with ZipFile(temporary) as z: assert z.testzip() is None
        temporary.replace(path)
    finally:temporary.unlink(missing_ok=True)

def main():
    package=ROOT/'cram_studio';manifest=json.loads((package/'manifest.json').read_text())
    assert manifest['package']=='cram_studio'
    version=manifest['version'];out=ROOT/'dist';out.mkdir(exist_ok=True)
    (package/'README.md').write_bytes((ROOT/'README.md').read_bytes())
    addon={name:(package/name).read_bytes() for name in FILES}
    for name,data in addon.items():
        if name.endswith('.py'):compile(data,name,'exec')
    installer=out/f'Cram-Studio-v{version}.ankiaddon';archive(installer,addon)
    checks={f'cram_studio/{name}':hashlib.sha256(data).hexdigest() for name,data in addon.items()}
    checks[installer.name]=hashlib.sha256(installer.read_bytes()).hexdigest()
    handoff={f'cram_studio/{name}':data for name,data in addon.items()}
    handoff.update({name:(ROOT/name).read_bytes() for name in DOCS})
    handoff['dist/'+installer.name]=installer.read_bytes()
    checks={name:hashlib.sha256(data).hexdigest() for name,data in handoff.items()}
    handoff['CHECKSUMS.json']=(json.dumps(checks,indent=2)+'\n').encode()
    bundle=out/f'Cram-Studio-Handoff-v{version}.zip';archive(bundle,handoff)
    print(json.dumps([{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (installer,bundle)],indent=2))

if __name__=='__main__':main()
