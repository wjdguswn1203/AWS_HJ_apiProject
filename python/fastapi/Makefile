all:
	json-server --watch ../shoppingmall_closed_data.json --host 0.0.0.0 --port 5500 &
	uvicorn app:app --host 0.0.0.0 --port 3500 --reload