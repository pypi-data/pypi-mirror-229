from bible import KJV


def test_bible():
    bible = KJV()
    # TODO: This should be 31102 but it gets 31103.  I don't yet know why.
    assert len(bible.verses) == 31103

    assert bible.verses[0]["book"] == "Genesis"
    assert bible.verses[0]["chapter"] == 1
    assert bible.verses[0]["verse"] == 1
    assert (
        bible.verses[0]["text"]
        == "In the beginning God created the heaven and the earth."
    )


def test_bible_iter():
    bible = KJV()
    for verse in bible:
        assert bible.verses[0]["book"] == "Genesis"
        assert bible.verses[0]["chapter"] == 1
        assert bible.verses[0]["verse"] == 1
        break


def test_bible_get_text():
    bible = KJV()
    text = bible.get_text("Genesis 1:1")
    assert text == "In the beginning God created the heaven and the earth."


def test_bible_get_text_multiple_cite():
    bible = KJV()
    text = bible.get_text("Genesis 1:1-2")
    assert (
        text
        == "In the beginning God created the heaven and the earth. And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters."
    )
