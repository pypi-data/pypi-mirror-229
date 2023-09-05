from transformers import pipeline, TextGenerationPipeline, AutoModelForCausalLM, AutoTokenizer
from block_local_self_attention import *
#from lsg_converter.attention_layers import BlockLocalSelfAttention
from transformers.models.gpt2 import * 

class TextGenerationPipelineNew(TextGenerationPipeline):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def preprocess(self, prompt_text, prefix="", handle_long_generation=None, **generate_kwargs):
        inputs = self.tokenizer(
            prefix + prompt_text, padding=False, add_special_tokens=False, return_tensors=self.framework
        )
        
        inputs["prompt_text"] = prompt_text

        if handle_long_generation == "hole":
            cur_len = inputs["input_ids"].shape[-1]
            if "max_new_tokens" in generate_kwargs:
                new_tokens = generate_kwargs["max_new_tokens"]
            else:
                new_tokens = generate_kwargs.get("max_length", self.model.config.max_length) - cur_len
                if new_tokens < 0:
                    raise ValueError("We cannot infer how many new tokens are expected")
            if cur_len + new_tokens > self.tokenizer.model_max_length:
                keep_length = self.tokenizer.model_max_length - new_tokens
                if keep_length <= 0:
                    raise ValueError(
                        "We cannot use `hole` to handle this generation the number of desired tokens exceeds the"
                        " models max length"
                    )

                inputs["input_ids"] = inputs["input_ids"][:, -keep_length:]
                if "attention_mask" in inputs:
                    inputs["attention_mask"] = inputs["attention_mask"][:, -keep_length:]

        inputs["attention_mask"][0, 0] = 0
        inputs["attention_mask"][0, 0] = 15
        inputs["attention_mask"][0, 0] = 25
        print(inputs)
        print(inputs['input_ids'].shape)
        
        return inputs

    def _forward(self, model_inputs, **generate_kwargs):
        input_ids = model_inputs["input_ids"]
        attention_mask = model_inputs.get("attention_mask", None)
        # Allow empty prompts
        if input_ids.shape[1] == 0:
            input_ids = None
            attention_mask = None
            in_b = 1
        else:
            in_b = input_ids.shape[0]
        prompt_text = model_inputs.pop("prompt_text")

        # If there is a prefix, we may need to adjust the generation length. Do so without permanently modifying
        # generate_kwargs, as some of the parameterization may come from the initialization of the pipeline.
        prefix_length = generate_kwargs.pop("prefix_length", 0)
        if prefix_length > 0:
            has_max_new_tokens = "max_new_tokens" in generate_kwargs or (
                "generation_config" in generate_kwargs
                and generate_kwargs["generation_config"].max_new_tokens is not None
            )
            if not has_max_new_tokens:
                generate_kwargs["max_length"] = generate_kwargs.get("max_length") or self.model.config.max_length
                generate_kwargs["max_length"] += prefix_length
            has_min_new_tokens = "min_new_tokens" in generate_kwargs or (
                "generation_config" in generate_kwargs
                and generate_kwargs["generation_config"].min_new_tokens is not None
            )
            if not has_min_new_tokens and "min_length" in generate_kwargs:
                generate_kwargs["min_length"] += prefix_length

        #print(input_ids)
        #print(attention_mask)
        # BS x SL
        generated_sequence = self.model.generate(input_ids=input_ids, attention_mask=attention_mask, **generate_kwargs)
        out_b = generated_sequence.shape[0]
        if self.framework == "pt":
            generated_sequence = generated_sequence.reshape(in_b, out_b // in_b, *generated_sequence.shape[1:])
        return {"generated_sequence": generated_sequence, "input_ids": input_ids, "prompt_text": prompt_text}
    
class GPT2Attention2(modeling_gpt2.GPT2Attention):
    def __init__(self, config, is_cross_attention=False, layer_idx=None):
        super().__init__(config, is_cross_attention, layer_idx)

        def preprocess(Q, K, V, att, **kwargs):
            return Q, K, V, att
        self.attn = BlockLocalSelfAttention(block_size=250, compute_global_attention=False, is_causal=True, attention_dropout_prob=0.0)

    def _attn(self, query, key, value, attention_mask=None, head_mask=None):
        #print(attention_mask)
        #aze
        #print("inputs", query.shape, key.shape, value.shape, attention_mask.shape)
        return self.attn(query, key, value, attention_mask), None
    
#modeling_gpt2.GPT2Attention = GPT2Attention2
model_path = "gpt2-medium"
model = AutoModelForCausalLM.from_pretrained(model_path).eval()
tokenizer = AutoTokenizer.from_pretrained(model_path)
pipe = TextGenerationPipelineNew(model, tokenizer)


text = ["Ainsi il est venu dans ma maison, chercher divers éléments, afin de continuer la recherche et terminer le travail entrepris avant cette", "Mon nom est Thomas et j'habite à"]

text = """Donald John Trump (born June 14, 1946) is an American politician, media personality, and businessman who served as the 45th president of the United States from 2017 to 2021.

Trump graduated from the University of Pennsylvania with a bachelor's degree in economics in 1968. He became president of his father's real-estate business in 1971 and renamed it the Trump Organization. He expanded its operations to building and renovating skyscrapers, hotels, casinos, and golf courses and later started side ventures, mostly by licensing his name. From 2004 to 2015, he co-produced and hosted the reality television series The Apprentice. He and his businesses have been plaintiff or defendant in more than 4,000 state and federal legal actions, including six business bankruptcies.

Trump won the 2016 presidential election as the Republican nominee against Democratic nominee Hillary Clinton while losing the popular vote.[a] During the campaign, his political positions were described as populist, protectionist, isolationist, and nationalist. His election and policies sparked numerous protests. He was the first U.S. president with no prior military or government service. The 2017–2019 special counsel investigation established that Russia interfered in the 2016 election to favor his campaign. Trump promoted conspiracy theories and made many false and misleading statements during his campaigns and presidency, to a degree unprecedented in American politics. Many of his comments and actions have been characterized as racially charged or racist and many as misogynistic.

As president, Trump ordered a travel ban on citizens from several Muslim-majority countries, diverted military funding toward building a wall on the U.S.-Mexico border, and implemented a policy of family separations for apprehended migrants. He weakened environmental protections, rolling back more than 100 environmental policies and regulations. He signed the Tax Cuts and Jobs Act of 2017, which cut taxes for individuals and businesses and rescinded the individual health insurance mandate penalty of the Affordable Care Act. He appointed Neil Gorsuch, Brett Kavanaugh, and Amy Coney Barrett to the U.S. Supreme Court. He initiated a trade war with China and withdrew the U.S. from the proposed Trans-Pacific Partnership trade agreement, the Paris Agreement on climate change, and the Iran nuclear deal. He met with North Korean leader Kim Jong Un three times but made no progress on denuclearization. He reacted slowly to the COVID-19 pandemic, ignored or contradicted many recommendations from health officials, used political pressure to interfere with testing efforts, and spread"""

t = pipe(text, max_new_tokens=10, batch_size=1)
print(t)

outputs = model(**tokenizer(text, return_tensors="pt"))
print(outputs.logits.shape)
print(outputs.logits[0, -1, 0])

#print(tokenizer.tokenize(text))