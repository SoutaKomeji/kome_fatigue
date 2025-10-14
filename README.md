# 下準備

Python(ver3.13.7)

Dockerを起動しておく(緯度経度高度データの保存に必要　データが存在するなら不要)

仮想環境を作成 & 有効化
```
python3 -m venv venv
source venv/bin/activate
```

# パッケージのインストール方法
```
pip install -r requirements.txt
```

# 実行方法
```
python nsga3_fatigue.py
```
実行後，世代数を聞かれるので，任意の世代数をターミナルで入力するとGAが実行されます

```
python spot_name_list_steps.py
```
これは提案されたルート番号（例：56, 21, 2, 41, 20, 45, 56）をターミナルに入力すると，
観光スポット名と，そのスポットの特徴量や滞在時間などがわかります
