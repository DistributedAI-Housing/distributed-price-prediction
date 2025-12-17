import grpc
import time

class TimingInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        start_time = time.time()
        response = continuation(handler_call_details)
        end_time = time.time()
        print(f"[TIMING] {handler_call_details.method} exécuté en {end_time - start_time:.4f}s")
        return response
