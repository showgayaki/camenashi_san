from logging import getLogger
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

from database.models import Toilet, Category


logger = getLogger('bot')
# クロスプラットフォーム対応の日本語フォントを設定
rcParams['font.family'] = 'Noto Sans CJK JP'


def draw_toilet_records(label: str, period: str, records: list[Toilet], categories: list[Category]) -> Path:
    category_names = [category.name for category in categories]
    logger.info(f'category_names: {category_names}')

    data = {
        'datetime': [record.created_at for record in records],
        'type': [record.category.name for record in records],
    }

    # データフレームの作成
    df = pd.DataFrame(data)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['date'] = df['datetime'].dt.date
    # 年を除いた日付フォーマットに変換
    df['formatted_date'] = df['datetime'].dt.strftime('%m-%d')

    # 集計
    summary = df.groupby(['formatted_date', 'type']).size().unstack(fill_value=0)
    # すべてのカテゴリを含める
    for category in category_names:
        if category not in summary.columns:
            summary[category] = 0  # データがないカテゴリを0で補完

    # 列の順序を category_names に合わせる
    summary = summary[category_names]

    # 色を固定
    color_mapping = {
        category.name: category.graph_color for category in categories
    }
    # グラフの作成
    plt.figure(figsize=(10, 6))
    for category in summary.columns:
        plt.plot(
            summary.index,  # 横軸
            summary[category],  # 縦軸
            label=category,  # 凡例用
            color=color_mapping.get(category, 'gray'),  # 色の指定、デフォルトは灰色
            marker='o',  # マーカーを丸に設定
            linestyle='-',  # 線のスタイル
        )

    plt.title(f'{label}のおトイレ回数')
    plt.ylabel('回数')
    plt.xlabel('日時')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    # 縦軸を整数に設定
    y_max = summary.values.max() + 1
    plt.yticks(range(0, y_max))

    plt.legend()
    plt.tight_layout()

    # 保存ディレクトリなかったら作成
    output_dir = Path(__file__).parent.parent.joinpath('output')
    if output_dir.exists() is False:
        output_dir.mkdir()

    # グラフの保存
    output_path = Path(output_dir).joinpath(f'{period}.png')
    logger.info(f'Graph saved to {output_path}')

    plt.savefig(output_path, dpi=300, bbox_inches='tight')  # ファイルを保存
    return output_path
