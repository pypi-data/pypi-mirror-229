from pydantic import BaseModel, Field
from typing import Optional, Literal, Union, List, Dict, NewType

FileField = NewType('FileField', str)

class LLMInputModel1(BaseModel):
    """
    Supports Following models: Falcon-40B-instruct, Falcon-7B-instruct, openllama-13b-base, llama2-7b-chat

    prompt	string	Prompt is a textual instruction for the model to produce an output.	Required
    top_k	integer	Top-k sampling helps improve quality by removing the tail and making it less likely to go off topic.	Optional
    (Default: 40)
    top_p	float	Top-p sampling helps generate more diverse and creative text by considering a broader range of tokens.	Optional
    (Default: 1.0)
    temp	float	The temperature influences the randomness of the next token predictions.	Optional
    (Default: 0.98)
    max_length	integer	The maximum length of the generated text.	Optional
    (Default: 256)
    repetition_penalty	float	The model uses this penalty to discourage the repetition of tokens in the output.	Optional
    (Default: 1.2)
    beam_size	integer	The beam size for beam search. A larger beam size results in better quality output, but slower generation times.	Optional
    (Default: 1)    
    """
    prompt: str
    top_k: int = 40
    top_p: float = Field(0.9, ge=0., le=1.)
    temp: float = Field(0.98, ge=0., le=1.)
    max_length: int = 256
    repetition_penalty: float = 1.2
    beam_size: int = 1


class LLMInputModel2(BaseModel):
    """
    Supports Following models: MPT-30B-instruct, MPT-7B-instruct

    prompt:	string	Instruction is a textual command for the model to produce an output.	Required
    top_k	integer	Top-k sampling helps improve quality by removing the tail and making it less likely to go off topic.	Optional
    (Default: 40)
    top_p	float	Top-p sampling helps generate more diverse and creative text by considering a broader range of tokens.	Optional
    Allowed Range: 0 - 1
    (Default: 1.0)
    temp	float	Temperature is a parameter that controls the randomness of the model's output. The higher the temperature, the more random the output.	Optional
    (Default: 0.98)
    max_length	integer	Maximum length of the generated output.	Optional
    (Default: 256)
    """
    prompt: str
    top_k: int = 40
    top_p: float = Field(0.9, ge=0., le=1.)
    temp: float = Field(0.98, ge=0., le=1.)
    max_length: int = 256

class SDInputModel(BaseModel):
    """
    Support following models: text2img, text2img-sdxl

    prompt:	string	Your input text prompt	Required
    negprompt:	string	Negative text prompt	Optional
    samples:	integer	No. of images to be generated. Allowed range: 1-4	Optional
    (Default: 1)
    steps:	integer	Sampling steps per image. Allowed range 30-500	Optional
    (Default: 30)
    aspect_ratio: string.  Allowed values: square, landscape, portrait	Optional
    (Default: square)
    guidance_scale:	float.	Prompt guidance scale	Optional
    (Default: 7.5)
    seed:	integer	Random number used to initialize the image generation.	Optional
    (Default: random)
    """
    prompt: str
    negprompt: Optional[str] = ""
    samples: Optional[int] = Field(1, ge=1, le=4)
    steps: Optional[int] = Field(30, ge=30, le=500)
    aspect_ratio: Optional[Literal['square', 'landscape', 'portrait']] = 'square'
    guidance_scale: Optional[float] = 7.5
    seed: Optional[int] = None

class Img2Img(BaseModel):
    """
    Support following models: img2img

    prompt:	string	Your input text prompt	Required
    negprompt:	string	Negative text prompt	Optional
    steps:	integer	Sampling steps per image. Allowed range 30-500	Optional
    (Default: 30)
    init_image_url:	string	Original Image URL or local file is Required
    strength:	float.	Controls how much the original image will be modified.	Optional
    (Default: 0.75)
    guidance_scale:	float.	Prompt guidance scale	Optional
    (Default: 12.5)
    seed:	integer	Random number used to initialize the image generation.	Optional
    (Default: random)
    """
    prompt: str
    negprompt: Optional[str] = ""
    steps: Optional[int] = Field(30, ge=30, le=500)
    init_image_url: FileField
    strength: Optional[float] = Field(0.75, ge=0.0, le=1.0)
    guidance_scale: Optional[float] = 7.5
    seed: Optional[int] = None

class Pix2Pix(BaseModel):
    """
    Support following models: pix2pix

    prompt:	string	Your input text prompt	Required
    negprompt:	string	Negative text prompt	Optional
    steps:	integer	Sampling steps per image. Allowed range 30-500	Optional
    (Default: 30)
    init_image_url:	string	Original Image URL or local file is Required
    guidance_scale:	float.	Prompt guidance scale	Optional
    (Default: 12.5)
    image_guidance_scale:	float.	Prompt guidance scale	Optional
    (Default: 1.5)
    seed:	integer	Random number used to initialize the image generation.	Optional
    (Default: random)
    """
    prompt: str
    negprompt: Optional[str] = ""
    steps: Optional[int] = Field(30, ge=30, le=500)
    init_image_url: FileField
    guidance_scale: Optional[float] = Field(7.5, ge=5, le=50)
    image_guidance_scale: Optional[float] = Field(1.5, ge=0, le=5)
    seed: Optional[int] = None

class Txt2Speech(BaseModel):
    """
    Support following models: Txt2Speech

    prompt:	string	Prompt is a text string that is going to be converted to an audio file	Required
    speaker:	string	Defines the language and speaker for speech.	Optional
    sample_rate:	int	Sampling rate for output audio.	Optional
    (Default: 25000)
    text_temp:	float.	Temperature setting for text prompt. Supported range: 0.1 to 1.0	Optional
    (Default: 0.5)
    waveform_temp:	float.	Temperature setting for audio waveform. Supported range: 0.1 to 1.0	Optional
    (Default: 0.5)
    """
    prompt: str
    speaker: Optional[str]
    sample_rate: Optional[int] = 25000
    text_temp: Optional[float] = Field(0.5, ge=0.1, le=1.0)
    waveform_temp: Optional[float] = Field(0.5, ge=0.1, le=1.0)

class Speech2Txt(BaseModel):
    """
    Support following models: whisper

    file:	string	URL of a file or local file that that needs to be transcribed.	Required
    diarize:	bool	When diarize is set to true, an embedding model will be employed to identify speakers, along with their respective transcripts and durations	Optional
    transcription_format: string Defines the output format.
    prompt: string	Initial prompt to the whisper model for recognizing words correctly.
    You can pass a comma separated list of words.
    remove_silence:	bool  If set as true, it will use VAD (Voice Activity Detection) filter to remove silent parts of the audio and then perform transcript with only audible parts.
    language:	string.	Defines the language for transcription output. Translates the transcript to your preferred language.
    num_speakers: int  It specifies the expected number of speakers present in the audio file and is used in conjunction with the "diarize" parameter, which enables speaker diarization
    """
    file: FileField
    diarize: Optional[bool] = False
    transcription_format: Optional[str] = 'text'
    prompt: Optional[str] = ''
    remove_silence: Optional[bool] = False
    language: Optional[str] = 'en'
    num_speakers: Optional[int] = Field(2, ge=1, le=11)

MODELS_TO_DATAMODEL = {
            'falcon-7b-instruct': LLMInputModel1,
            'falcon-40b-instruct': LLMInputModel1,
            'mpt-7b-instruct': LLMInputModel2,
            'mpt-30B-instruct': LLMInputModel2,
            'llama2-7b-chat': LLMInputModel1,
            "sdxl-base": SDInputModel,
            "txt2img": SDInputModel,
            "img2img" : Img2Img,
            "pix2pix" : Pix2Pix,
            "sunoai-bark" : Txt2Speech,
            "whisper" : Speech2Txt        }

MODEL_TYPES = { 
                    "falcon-7b-instruct": "LLM",
                    "falcon-40b-instruct": "LLM",
                    "mpt-30B-instruct": "LLM",
                    "mpt-7b-instruct": "LLM",
                    "llama2-7b-chat": "LLM",
                    "sdxl-base": "TEXT-TO-IMG",
                    "txt2img": "TEXT-TO-IMG"
                    }