from torch.optim import Adam, AdamW


def get_optimizer(optim, model, lr):
    if optim == 'adam':
        return Adam(model.parameters(), lr=lr)
    elif optim == 'adamw':
        return AdamW(model.parameters(), lr=lr)
    else:
        raise RuntimeError('unknown optimizer type')


def init_bert_and_tokenizer(checkpoint=)
