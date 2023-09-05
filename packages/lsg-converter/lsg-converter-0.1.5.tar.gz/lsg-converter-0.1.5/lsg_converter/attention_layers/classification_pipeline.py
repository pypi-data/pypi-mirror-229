from transformers import pipeline, TextGenerationPipeline, AutoModelForCausalLM, AutoTokenizer, TextClassificationPipeline, AutoModelForSequenceClassification
from block_local_self_attention import *
#from lsg_converter.attention_layers import BlockLocalSelfAttention
from transformers.models.distilbert import * 

class GPT2Attention2(modeling_distilbert.MultiHeadSelfAttention):
    def __init__(self, config):
        super().__init__(config)

        self.attn = BlockLocalSelfAttention(block_size=16, compute_global_attention=True, is_causal=False, attention_dropout_prob=0.0)

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: torch.Tensor,
        head_mask = None,
        output_attentions = False,
    ):
        """
        Parameters:
            query: torch.tensor(bs, seq_length, dim)
            key: torch.tensor(bs, seq_length, dim)
            value: torch.tensor(bs, seq_length, dim)
            mask: torch.tensor(bs, seq_length)

        Returns:
            weights: torch.tensor(bs, n_heads, seq_length, seq_length) Attention weights context: torch.tensor(bs,
            seq_length, dim) Contextualized layer. Optional: only if `output_attentions=True`
        """
        bs, q_length, dim = query.size()
        k_length = key.size(1)
        # assert dim == self.dim, f'Dimensions do not match: {dim} input vs {self.dim} configured'
        # assert key.size() == value.size()

        dim_per_head = self.dim // self.n_heads

        mask_reshp = (bs, 1, 1, k_length)

        def shape(x: torch.Tensor) -> torch.Tensor:
            """separate heads"""
            return x.view(bs, -1, self.n_heads, dim_per_head).transpose(1, 2)

        def unshape(x: torch.Tensor) -> torch.Tensor:
            """group heads"""
            return x.transpose(1, 2).contiguous().view(bs, -1, self.n_heads * dim_per_head)

        q = shape(self.q_lin(query))  # (bs, n_heads, q_length, dim_per_head)
        k = shape(self.k_lin(key))  # (bs, n_heads, k_length, dim_per_head)
        v = shape(self.v_lin(value))  # (bs, n_heads, k_length, dim_per_head)

        """
        q = q / math.sqrt(dim_per_head)  # (bs, n_heads, q_length, dim_per_head)
        scores = torch.matmul(q, k.transpose(2, 3))  # (bs, n_heads, q_length, k_length)
        mask = (mask == 0).view(mask_reshp).expand_as(scores)  # (bs, n_heads, q_length, k_length)
        scores = scores.masked_fill(
            mask, torch.tensor(torch.finfo(scores.dtype).min)
        )  # (bs, n_heads, q_length, k_length)
        
        weights = nn.functional.softmax(scores, dim=-1)  # (bs, n_heads, q_length, k_length)
        weights = self.dropout(weights)  # (bs, n_heads, q_length, k_length)

        # Mask heads if we want to
        if head_mask is not None:
            weights = weights * head_mask

        context = torch.matmul(weights, v)  # (bs, n_heads, q_length, dim_per_head)
        context = unshape(context)  # (bs, q_length, dim)
        """
        
        context = self.attn(q, k, v, None)
        context = unshape(context)  # (bs, q_length, dim)
        context = self.out_lin(context)  # (bs, q_length, dim)

        return (context,)
        
    
modeling_distilbert.MultiHeadSelfAttention = GPT2Attention2
model_path = "lvwerra/distilbert-imdb"
model = AutoModelForSequenceClassification.from_pretrained(model_path).eval()
tokenizer = AutoTokenizer.from_pretrained(model_path)
pipe = pipeline("text-classification", model=model, tokenizer=tokenizer)


text = """I saw the Mogul Video VHS of this. That's another one of those old 1980s distributors whose catalog I wish I had!<br /><br />This movie was pretty poor. Though retitled "Don't Look in the Attic," the main admonition that is repeated in this is "Don't go to the villa." Just getting on the grounds of the villa is a bad idea. A character doesn't go into the attic until an hour into the movie, and actually should have done it earlier because of what is learned there.<br /><br />The movie starts in Turin, Italy in the 1950s. Two men are fighting, and a woman is telling them the villa is making them do it. One man kills the other, then regrets it, and the woman pulls out the knife and stabs him with it. She flees the villa, and after she's left a chair moves by itself (what's the point of that?), but when in the garden a hand comes up through the ground and drags he into the earth.<br /><br />From there, it's the present day, thirty years later. There's a séance that appears suddenly and doesn't appear to have anything to do with the movie. The children of the woman from the prologue are inheriting the house. The main daughter is played by the same actress who played her mother. At least one of the two men from the prologue seems to reoccur as another character too. She's haunted by some warnings not to go to the villa, but they all do, since if they do not use it, they forfeit it. People die. A lawyer who has won all his cases tries to investigate a little. The ending is pretty poor. Why was the family cursed? An unfortunately boring movie.<br /><br />There's an amusing small-print disclaimer on the back of the video box that reads "The scenes depicted on this packaging may be an artist's impression and may not necessarily represent actual scenes from the film." In this case, the cover of the box is an illustration that does more or less accurately depict the aforementioned woman dragged underground scene, although there are two hands, and the woman is different. It's true, sometimes the cover art has nothing to do with the movie. I also recall seeing a reviewer who had a bad movie predictor scale, in which movies with illustrations on the cover instead of photos got at least one point for that."""
t = pipe(text, batch_size=1, truncation=True)
print(t)

outputs = model(**tokenizer(text, return_tensors="pt", truncation=True))
print(outputs.logits.shape)
print(outputs.logits[0, -1, 0])

#print(tokenizer.tokenize(text))