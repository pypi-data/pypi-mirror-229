import click
import os
import configparser as cfg


def load_streamlit_config(dirname):
    config = cfg.ConfigParser()
    config.optionxform = str
    config.read(os.path.join(dirname, "config.ini"))
    config = {s: dict(config.items(s)) for s in config.sections()}
    return config


def conv_config_to_args(config):
    # translate config to streamlit args
    args = []
    for k, v in config.items():
        for kk, vv in v.items():
            args.append('--' + k + '.' + kk)
            args.append(vv)
    return args


@click.group()
def main():
    pass


@main.command("gui")
def main_streamlit():
    dirname = os.path.dirname(__file__)
    config = load_streamlit_config(dirname)
    args = conv_config_to_args(config)
    filename = os.path.join(dirname, 'main.py')
    os.system('streamlit run ' + filename + ' ' + ' '.join(args))


if __name__ == "__main__":
    main()