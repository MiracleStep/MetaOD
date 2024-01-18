import json

# JSON字符串
json_str = """{
  "responses": [
    {
      "localizedObjectAnnotations": [
        {
          "mid": "/m/01bqk0",
          "name": "Bicycle wheel",
          "score": 0.94234306,
          "boundingPoly": {
            "normalizedVertices": [
              {
                "x": 0.31524897,
                "y": 0.78658724
              },
              {
                "x": 0.44186485,
                "y": 0.78658724
              },
              {
                "x": 0.44186485,
                "y": 0.9692919
              },
              {
                "x": 0.31524897,
                "y": 0.9692919
              }
            ]
          }
        },
        {
          "mid": "/m/01bqk0",
          "name": "Bicycle wheel",
          "score": 0.9337022,
          "boundingPoly": {
            "normalizedVertices": [
              {
                "x": 0.50342137,
                "y": 0.7553652
              },
              {
                "x": 0.6289583,
                "y": 0.7553652
              },
              {
                "x": 0.6289583,
                "y": 0.9428141
              },
              {
                "x": 0.50342137,
                "y": 0.9428141
              }
            ]
          }
        },
        {
          "mid": "/m/0199g",
          "name": "Bicycle",
          "score": 0.8973106,
          "boundingPoly": {
            "normalizedVertices": [
              {
                "x": 0.31594256,
                "y": 0.66489404
              },
              {
                "x": 0.63338375,
                "y": 0.66489404
              },
              {
                "x": 0.63338375,
                "y": 0.9687162
              },
              {
                "x": 0.31594256,
                "y": 0.9687162
              }
            ]
          }
        },
        {
          "mid": "/m/06z37_",
          "name": "Picture frame",
          "score": 0.7171168,
          "boundingPoly": {
            "normalizedVertices": [
              {
                "x": 0.7882889,
                "y": 0.16610023
              },
              {
                "x": 0.9662418,
                "y": 0.16610023
              },
              {
                "x": 0.9662418,
                "y": 0.3178568
              },
              {
                "x": 0.7882889,
                "y": 0.3178568
              }
            ]
          }
        }
      ]
    }
  ]
}
"""

# 使用json.loads将JSON字符串转换为Python对象（字典）
objects = json.loads(json_str)
from PIL import Image
im = Image.open("bicycle_example.png")
w, h = im.size
# 打印转换后的Python对象
print(objects)
res = []
for object_ in objects["responses"][0]["localizedObjectAnnotations"]:
    # print('\n{} (confidence: {})'.format(object_.name, object_.score))
    # print('Normalized bounding polygon vertices: ')

    # for vertex in object_.bounding_poly.normalized_vertices:
    #    print(' - ({}, {})'.format(vertex.x, vertex.y))

    c = 0
    for vertex in object_["boundingPoly"]["normalizedVertices"]:
        c += 1
        if c == 1:
            x0 = int(vertex["x"] * w)
            y0 = int(vertex["y"] * h)
        elif c == 3:
            x1 = int(vertex["x"] * w)
            y1 = int(vertex["y"] * h)
    if (x0 == 0):
        x0 = 10
    if (x1 == 0):
        x1 = 10
    if (y0 == 0):
        y0 = 10
    if (y1 == 0):
        y1 = 10
    box = ((x0, x1), (y0, y1))
    n = object_["name"]
    n = n.replace(" ", "_")
    res.append((n, object_["score"] * 100, box))

print(res)
