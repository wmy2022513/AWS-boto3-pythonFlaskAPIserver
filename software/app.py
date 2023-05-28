from flask import Flask, jsonify, request, render_template, redirect
# import requests
app = Flask(__name__)

pets = [
  {
    "id": 1,
    "name": "Shiba Inu",
    "type": "dog",
    "breed": "small-to-medium",
    "price": 22.99 
  },
  {
    "id": 2,
    "name": "Siberian Husky",
    "type": "dog",
    "breed": "Spitz genetic",
    "price": 54.99 
  },
  {
    "id": 3,
    "name": "Bernese Mountain",
    "type": "dog",
    "breed": "Sennenhund-type",
    "price": 74.99 
  },
  {
    "id": 4,
    "name": "Persian longhair",
    "type": "cat",
    "breed": "long-haired",
    "price": 74.99 
  },
  {
    "id": 5,
    "name": "Bombay cat",
    "type": "cat",
    "breed": "short-haired",
    "price": 104.99 
  }
]

#curl http://localhost:5000
@app.get('/')
def index():
#   return render_template('index.html', pets = pets)
  return render_template('index.html', pets = pets)
@app.get('/pets')
def pets_page():
#   return render_template('updateItem.html', pets = pets)
  return jsonify(pets)

#curl http://localhost:5000/book/1
@app.get('/pets/<int:id>')
def get_pets(id):
  for pet in pets:
    if pet["id"] == id:
        return jsonify(pet)
  return f'Pet with id {id} not found', 404

@app.get('/add_page')
def add_page():
  return render_template('addItem.html')

@app.post('/add_item')
def add_item():
  new_id = int(request.form['id'])
  new_name = request.form['name']
  new_type = request.form['type']
  new_breed = request.form['breed']
  new_price = request.form['price']
  new_pet = {"id": new_id, "name": new_name, "type": new_type, "breed": new_breed, "price": new_price }
  pets.append(new_pet)
  return redirect('/')

#curl http://localhost:5000/update_item/2 --request POST --data '{"author":"ccc","title":"ddd","price":999.99}' --header "Content-Type: application/json"
@app.route('/update_item/<int:id>', methods=['GET','POST'])
def update_item(id):  
  for pet in pets:
    if pet["id"] == id:
        if request.method=="POST":
          pet["id"] = int(request.form['id'])
          pet["name"] = request.form['name']
          pet["type"] = request.form['type']
          pet["breed"] = request.form['breed']
          pet["price"] = float(request.form['price'])
          return redirect('/')
        else:
          return render_template('updateItem.html', pet = pet)
  return f'Pet with id {id} not found', 404

#curl http://localhost:5000/delete_book/1 --request DELETE
@app.route('/delete_item/<int:id>', methods=['GET','POST'])
def delete_item(id):
  for pet in pets:
    if pet["id"] == id:
        if request.method=="POST":
          pets.remove(pet)
          return redirect('/')
        else:
          return render_template('deleteItem.html', pet = pet)
  return f'Pet with id {id} not found', 404

