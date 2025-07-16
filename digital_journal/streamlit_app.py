import streamlit.web.cli as stcli # type: ignore
import sys

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "app/main.py"]
    sys.exit(stcli.main())
