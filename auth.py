from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import MongoClient

router = APIRouter()

mongo_uri = "mongodb+srv://devguru13580:hXcQgMDBinZ8wlo4@cluster0.ehilact.mongodb.net/"
client = MongoClient(mongo_uri)

# Create a database object
db = client["harmony"]

# Define MongoDB collection for users
users_collection = db["users"]

class UserSignIn(BaseModel):
    email: str
    password: str

class UserSignUp(BaseModel):
    username: str
    email: str
    password: str

@router.post("/signin")
def sign_in(user: UserSignIn):
    # Find the user by email and password in the MongoDB collection
    result = users_collection.find_one({"email": user.email, "password": user.password})

    if result:
        return {"message": "Sign-in successful", "name": result["username"], "mail": result["email"], "level": result["lvl"], "expire": result["expire_day"]}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/signup")
def sign_up(user: UserSignUp):
    # Check if the username or email already exists in the MongoDB collection
    existing_user = users_collection.find_one({"$or": [{"username": user.username}, {"email": user.email}]})

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Insert the new user into the MongoDB collection
    new_user = {
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "lvl": 0,
        "expire_day": None
    }
    users_collection.insert_one(new_user)

    return {"message": "Sign-up successful"}

@router.get("/")
def helps():
    print("Running")
    return {"message": "Connection successful"}


@router.post("/create-checkout-session")
async def create_checkout_session():
    session = await stripe.checkout.sessions.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "T-shirt",
                    },
                    "unit_amount": 2000,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="localhost:8000/home",
        cancel_url="localhost:8000/pricing",
    )
    return JSONResponse(content={"url": session.url})

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.json()  # This line extracts the JSON payload from the request

    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, "we_1OCOuVItQ91j83DiPPMX5hgi"
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail=f"Invalid signature: {e}")

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        # Payment succeeded, update your database or perform other actions
        print('Payment succeeded!')

    return {"status": "success"}
