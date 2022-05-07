from pathlib import Path
from joblib import dump

import click
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from .models import create_pipeline


def get_dataset(
        dataset_path: Path
) -> pd.DataFrame:
    if dataset_path.suffix != '.csv':
        raise TypeError(
            'Data profiling does not support '
            'anything other than .csv data extension')
    df = pd.read_csv(dataset_path)
    df.columns = df.columns.str.lower()
    df.set_index('id', inplace=True)
    return df


def get_dataset_xy(dataset_path: Path
                   ) -> tuple[pd.DataFrame, pd.Series]:
    df = get_dataset(dataset_path)
    return df.drop(columns='cover_type'), df['cover_type']


@click.command()
@click.option(
    "-d",
    "--dataset-path",
    default="data/train.csv",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    show_default=True,
)
@click.option(
    "-s",
    "--save-model-path",
    default="data/model.joblib",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    show_default=True,
)
@click.option(
    "-m",
    "--model",
    default="knn",
    type=click.Choice(['knn'], case_sensitive=False),
    show_default=True,
)
@click.option(
    "--random-state",
    default=42,
    type=int,
    show_default=True,
)
@click.option(
    "--test-split-ratio",
    default=0.2,
    type=click.FloatRange(0, 1, min_open=True, max_open=True),
    show_default=True,
)
@click.option(
    "--knn-neighbors",
    default=5,
    type=click.IntRange(0, min_open=True),
    show_default=True,
)
def train(
        dataset_path: Path,
        save_model_path: Path,
        model: str,
        random_state: int,
        test_split_ratio: float,
        knn_neighbors: int,
):
    X_train, X_test, y_train, y_test = train_test_split(
        *get_dataset_xy(dataset_path),
        test_size=test_split_ratio,
        random_state=random_state
    )
    pipeline = create_pipeline(
        model=model,
        random_state=random_state,
        knn_neighbors=knn_neighbors,
    )
    pipeline.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, pipeline.predict(X_test))
    click.echo(f'Accuracy: {accuracy}')
    dump(pipeline, save_model_path)
