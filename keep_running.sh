while true
do
	if ! [[ $(ps -aux | grep "/root/miniconda3/bin/streamlit run main.py" | wc -l) == 2 ]]; then
		nohup streamlit run main.py --server.port 80 &
	fi

	sleep 1s

done
