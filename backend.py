
import random
import colorsys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier


BASE_COLOURS=["Red","Orange","Yellow","Green","Blue","Purple","Pink","Brown","Teal","Cyan","Magenta","Violet"]


def load_data(csv_path="color_pedia.csv"):
    df=pd.read_csv(csv_path)

    columns=["Color Name","HEX Code","Emotion","Mood","R","G","B"]
    df=df[columns].dropna().copy()

    def find_family(name):
        for colour in BASE_COLOURS:
            if colour.lower() in str(name).lower():
                return colour
        return None

    df["Family"]=df["Color Name"].apply(find_family)
    df=df.dropna(subset=["Family"]).reset_index(drop=True)

    return df


def train_model(df):
    X=df[["R", "G", "B"]]
    y=df["Family"]

    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42)

    k=min(5,len(X_train))
    model=KNeighborsClassifier(n_neighbors=k)
    model.fit(X_train, y_train)

    accuracy=model.score(X_test, y_test)
    model.fit(X, y)

    return model,accuracy


def rgb_to_hex(r,g,b):
    return f"#{int(r):02X}{int(g):02X}{int(b):02X}"


def predict_colour(model,df,r,g,b):
    point=pd.DataFrame(
        [[r,g,b]],
        columns=["R","G","B"]
    )

    family=model.predict(point)[0]
    
    index=model.kneighbors(point,n_neighbors=1,return_distance=False)
    match=df.iloc[index[0][0]]

    return {
        "family": family,
        "match_name": match["Color Name"],
        "match_hex": match["HEX Code"],
        "emotion": match["Emotion"],
        "mood": match["Mood"],
        "selected_hex": rgb_to_hex(r, g, b)
    }


def matching_palette(r,g,b):
    h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255)

    colours=[
        ("Complementary",(h+0.5)%1),
        ("Analogous +",(h+1/12)%1),
        ("Analogous -",(h-1/12)%1),
        ("Triadic +",(h+1/3)%1),
        ("Triadic -",(h+2/3)%1)
    ]

    palette=[]

    for name,new_h in colours:
        rgb=colorsys.hsv_to_rgb(new_h, s, v)
        rgb=tuple(round(value * 255) for value in rgb)

        palette.append(
            {
            "label": name,
            "hex": rgb_to_hex(*rgb),
            "rgb": rgb
        })

    return palette


def random_rgb():
    return tuple(random.randint(0, 255) for _ in range(3))
