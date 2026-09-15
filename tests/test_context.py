"""Episode memory isolation and visible omission in saved studio handoffs."""
from studio.core import Studio


def test_context_preserves_all_current_episode_corrections_only(tmp_path):
    studio = Studio(tmp_path)
    studio.new('active', 'Active story', 'Creator thesis')
    studio.new('other', 'Other story', 'Different thesis')
    revoked = studio.feedback('active', 'REVOKED_CORRECTION', 'voice')
    studio.revoke(revoked['id'])
    for index in range(42):
        studio.feedback('active', f'ACTIVE_CORRECTION_{index:02d}', 'voice')
    for index in range(42):
        studio.feedback('other', f'UNRELATED_CORRECTION_{index:02d}', 'voice')

    context = studio.context('active')

    assert all(f'ACTIVE_CORRECTION_{index:02d}' in context for index in range(42))
    assert 'UNRELATED_CORRECTION' not in context
    assert 'REVOKED_CORRECTION' not in context
    assert context == studio.context('active')


def test_context_marks_long_authority_excerpt_and_preserves_short_file(tmp_path):
    studio = Studio(tmp_path)
    studio.new('active', 'Active story', 'Creator thesis')
    (tmp_path / 'PROJECT_CONTEXT.md').write_text('x' * 16000 + 'OMITTED_END', encoding='utf-8')
    (tmp_path / 'DECISIONS.md').write_text('Read the original decision.', encoding='utf-8')

    context = studio.context('active')

    assert 'x' * 16000 in context
    assert 'OMITTED_END' not in context
    assert '[Excerpt truncated; read PROJECT_CONTEXT.md in full before changing the project or relying on its contents.]' in context
    assert 'Read the original decision.' in context
    assert '[Excerpt truncated; read DECISIONS.md' not in context
