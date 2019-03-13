# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import explorer_pb2 as explorer__pb2
import inner_pb2 as inner__pb2


class InnerStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetPeerStatus = channel.unary_unary(
        '/protos.Inner/GetPeerStatus',
        request_serializer=explorer__pb2.EmptyRequest.SerializeToString,
        response_deserializer=inner__pb2.PeerStatusResponse.FromString,
        )


class InnerServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetPeerStatus(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_InnerServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetPeerStatus': grpc.unary_unary_rpc_method_handler(
          servicer.GetPeerStatus,
          request_deserializer=explorer__pb2.EmptyRequest.FromString,
          response_serializer=inner__pb2.PeerStatusResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'protos.Inner', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))