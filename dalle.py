import pickle
import jax
import random
import numpy as np
from PIL import Image
from time import time
import streamlit as st

import loghandler

LOG = loghandler.obtain("general", "general.log")

@st.cache(persist=True)
def generate_image_from_text(prompt, model_size="mini"):

    # Set cache to updated state to inform user that new results were returned
    st.session_state["cache_updated"] = True

    start = time()
    prompt = [prompt]
    
    # Ensure correct arguments
    if model_size not in ("mini", "mega"):
        raise ValueError("model_size must be one of 'mini' or 'mega'.")
    else:
        model_filename = f"artifacts/dalle{'_mini' * (model_size == 'mini')}.pkl"
    
    with open("artifacts/processor.pkl", "rb") as filehandler:
        processor = pickle.load(filehandler)

    try:
        with open(model_filename, "rb") as filehandler:
            model, params = pickle.load(filehandler)
    except ValueError:
        print(f"{model_filename} not found. Make sure you have run setup.py, passing in 'mega' as an argument if you want to use DALL·E Mega.")

    with open("artifacts/vqgan.pkl", "rb") as filehandler:
        vqgan, vqgan_params = pickle.load(filehandler)

    LOG.info("Model files read into memory. Generating encoded image...")
        
    tokenized_prompt = processor(prompt)

    # create a random key
    seed = random.randint(0, 2**32 - 1)
    key = jax.random.PRNGKey(seed)

    # We can customize generation parameters (see https://huggingface.co/blog/how-to-generate)
    top_k = None
    top_p = None
    temperature = None
    cond_scale = 10.0
    # generate image
    encoded_image = model.generate(
        **tokenized_prompt,
        prng_key=key,
        params=params,
        top_k=top_k,
        top_p=top_p,
        temperature=temperature,
        condition_scale=cond_scale,
    )
    # remove BOS
    encoded_image = encoded_image.sequences[..., 1:]

    LOG.info("Decoding image...")
    # decode image
    decoded_image = vqgan.decode_code(encoded_image, params=vqgan_params)
    decoded_image = decoded_image.clip(0.0, 1.0).reshape((256, 256, 3))

    image = Image.fromarray(np.asarray(decoded_image * 255, dtype=np.uint8))

    end = time()
    return round(end - start, 2), image