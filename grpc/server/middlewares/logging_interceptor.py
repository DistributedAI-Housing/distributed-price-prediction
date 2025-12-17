import grpc

class LoggingInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        print(f"[LOG] Appel méthode : {handler_call_details.method}")
        if handler_call_details.invocation_metadata:
            print(f"[LOG] Métadonnées : {handler_call_details.invocation_metadata}")
        return continuation(handler_call_details)
