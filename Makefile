all: fsm/s2t.json fsm/t2s.json

fsm/s2t.json: OpenCC/data/dictionary/STCharacters.txt OpenCC/data/dictionary/STPhrases.txt
	python opencc_fsm.py $^ -o $@

fsm/t2s.json: OpenCC/data/dictionary/TSCharacters.txt OpenCC/data/dictionary/TSPhrases.txt
	python opencc_fsm.py $^ -o $@

clean:
	rm fsm/*
