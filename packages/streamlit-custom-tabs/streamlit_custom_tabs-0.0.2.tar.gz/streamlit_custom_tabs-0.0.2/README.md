# streamlit_custom_tabs Component

Streamlit component that allows you to do X

## Installation instructions

```sh
pip install streamlit_custom_tabs
```

## Usage instructions

```python
import streamlit as st

from streamlit_custom_tabs import Tab_Bar


component1=  Tab_Bar(tabs=["Tab1","Tab2"],default=0,color="grey",activeColor="purple",fontSize="20px",key='bar')

#Handle your tabbar usecases here.
if(component1 == 0):
    st.write("Hooray! we are in Tab1")
else:
    st.write("Yippee! We are in Tab2 ")
```