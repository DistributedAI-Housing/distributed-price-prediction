import grpc
import jwt
from grpc import StatusCode

SECRET_KEY = "raron"

class AuthInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        # Skip auth for Signup/Login
        if handler_call_details.method in ["/api.AuthService/Login", "/api.AuthService/Signup"]:
            return continuation(handler_call_details)

        meta = dict(handler_call_details.invocation_metadata)
        token = meta.get("authorization")
        if not token:
            context = grpc.ServicerContext()
            context.abort(StatusCode.UNAUTHENTICATED, "Token manquant")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            handler_call_details.user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            context = grpc.ServicerContext()
            context.abort(StatusCode.UNAUTHENTICATED, "Token expiré")
        except jwt.InvalidTokenError:
            context = grpc.ServicerContext()
            context.abort(StatusCode.UNAUTHENTICATED, "Token invalide")

        return continuation(handler_call_details)
