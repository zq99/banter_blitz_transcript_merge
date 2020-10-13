

from transcript import merge_transcript


def main():
    file_name1 = "carlsen_commentary.txt"
    file_name2 = "firouzja_commentary.txt"
    merge_transcript(file_name1, file_name2, "carlsen", "firouzja", 0, 36)


if __name__ == '__main__':
    main()
