def get_recommendation_config(user):

    configs = user.configs
    if configs.count() < 1:
        return None

    default_config = configs.filter(is_default=True).first()
    if default_config:
        return default_config

    return configs.first()
