import random
random.seed(0)
import numpy as np
np.random.seed(0)
import itertools
import tensorflow as tf
import onnx_graphsurgeon as gs
from onnx2tf.utils.common_functions import (
    get_replacement_parameter,
    replace_parameter,
    convert_axis,
    get_constant_or_variable,
    print_node_info,
    inverted_operation_enable_disable,
    make_tf_node_info,
    pre_process_transpose,
    post_process_transpose,
    transpose_with_flexing_deterrence,
    shape_is_equal_ignore_order,
)


@print_node_info
@inverted_operation_enable_disable
@get_replacement_parameter
def make_node(
    *,
    graph_node: gs.Node,
    tf_layers_dict: dict,
    **kwargs: dict,
):
    """Concat

    Parameters
    ----------
    graph_node: gs.Node
        graph_surgeon Node

    tf_layers_dict: dict
        optype, shape, dtype, tensorflow graph
    """
    before_op_output_shape_trans = True
    for graph_node_input in graph_node.inputs:
        before_op_output_shape_trans_n = \
            tf_layers_dict.get(graph_node_input.name, {}).get('before_op_output_shape_trans', True)
        before_op_output_shape_trans = \
            before_op_output_shape_trans and before_op_output_shape_trans_n

    values = []
    nhwc_flags = []
    same_input_shape_as_onnxs = []
    for graph_node_input in graph_node.inputs:
        const_or_var = get_constant_or_variable(
            graph_node_input,
            before_op_output_shape_trans,
        )
        if isinstance(const_or_var, gs.Variable):
            values.append(tf_layers_dict[const_or_var.name]['tf_node'])
            nhwc_flags.append(
                tf_layers_dict[const_or_var.name]['nhwc'] \
                    if 'nhwc' in tf_layers_dict[const_or_var.name].keys() else False
            )
            same_input_shape_as_onnxs.append(
                True if graph_node_input.shape is not None and len(graph_node_input.shape) > 0 \
                    and graph_node_input.shape == tf_layers_dict[const_or_var.name]['tf_node'].shape else False
            )
        else:
            values.append(const_or_var)
            nhwc_flags.append(False)
            same_input_shape_as_onnxs.append(
                True if graph_node_input.shape is not None and len(graph_node_input.shape) > 0 \
                    and graph_node_input.shape == const_or_var.shape else False
            )

    # Shape Unmatched Special Avoidance Workaround
    # At least one True value for same_input_shape_as_onnx
    # At least one True value in nhwc_flags
    # same_input_shape_as_onnx == True and nhwc_flags == False and 3D or 4D or 5D tensor is NHWC transposed
    if True in same_input_shape_as_onnxs and True in nhwc_flags:
        before_op_output_shape_trans = True
        new_values = []
        for same_input_shape_as_onnx, nhwc_flag, value in zip(same_input_shape_as_onnxs, nhwc_flags, values):
            if same_input_shape_as_onnx and not nhwc_flag:
                if len(value.shape) == 3:
                    new_values.append(
                        transpose_with_flexing_deterrence(
                            input_tensor=value,
                            perm=[0,2,1],
                            **kwargs,
                        )
                    )
                elif len(value.shape) == 4:
                    new_values.append(
                        transpose_with_flexing_deterrence(
                            input_tensor=value,
                            perm=[0,2,3,1],
                            **kwargs,
                        )
                    )
                elif len(value.shape) == 5:
                    new_values.append(
                        transpose_with_flexing_deterrence(
                            input_tensor=value,
                            perm=[0,2,3,4,1],
                            **kwargs,
                        )
                    )
                else:
                    new_values.append(value)
            else:
                new_values.append(value)
        values = new_values

    graph_node_output: gs.Variable = graph_node.outputs[0]
    shape = graph_node_output.shape
    dtype = graph_node_output.dtype

    axis = graph_node.attrs.get('axis', 0)

    if len(values) == 2 \
        and ((not isinstance(values[0], np.ndarray) and isinstance(values[1], np.ndarray)) or (isinstance(values[0], np.ndarray) and not isinstance(values[1], np.ndarray))) \
        and sum([f for f in nhwc_flags]) == 0:

        variable_tensor = values[0] if not isinstance(values[0], np.ndarray) else values[1]
        constant_tensor = values[0] if isinstance(values[0], np.ndarray) else values[1]
        if hasattr(constant_tensor, '__len__'):
            tensor_candidate_for_transpositions = list(itertools.permutations(range(len(constant_tensor.shape))))
            new_values = []
            for tensor_candidate_for_transposition in tensor_candidate_for_transpositions:
                try:
                    _ = tf.concat(
                        values=[variable_tensor, constant_tensor.transpose(tensor_candidate_for_transposition)],
                        axis=axis
                    )
                    before_op_output_shape_trans = True
                    if not isinstance(values[0], np.ndarray):
                        new_values.append(values[0])
                        new_values.append(values[1].transpose(tensor_candidate_for_transposition))
                    else:
                        new_values.append(values[0].transpose(tensor_candidate_for_transposition))
                        new_values.append(values[1])
                    break
                except Exception as ex:
                    pass
            if new_values:
                values = new_values

    # NCHW->NHWC, NCDHW->NDHWC
    axis = convert_axis(
        axis=axis,
        tensor_rank=len(shape) if shape is not None else len(values[0].shape),
        before_op_output_shape_trans=before_op_output_shape_trans,
    )

    # Param replacement
    before_axis = axis
    axis = replace_parameter(
        value_before_replacement=axis,
        param_target='attributes',
        param_name='axis',
        **kwargs,
    )

    # Preserving Graph Structure (Dict)
    nhwc_judge = True
    for graph_node_input in graph_node.inputs:
        if isinstance(graph_node_input, gs.Variable) \
            and 'nhwc' in tf_layers_dict[graph_node_input.name].keys() \
            and tf_layers_dict[graph_node_input.name]['nhwc'] == True:
                nhwc_judge = nhwc_judge and True
        else:
            nhwc_judge = nhwc_judge and False

    # Set NHWC flag to True if all input tensors are determined by NHWC
    if nhwc_judge:
        tf_layers_dict[graph_node_output.name] = {
            'optype': graph_node.op,
            'shape': shape,
            'dtype': dtype,
            'nhwc': True,
        }
    else:
        tf_layers_dict[graph_node_output.name] = {
            'optype': graph_node.op,
            'shape': shape,
            'dtype': dtype,
        }

    # Generation of TF OP

    # Pre-process transpose
    new_values = []
    for graph_node_input, value in zip(graph_node.inputs, values):
        value = pre_process_transpose(
            value_before_transpose=value,
            param_target='inputs',
            param_name=graph_node_input.name,
            **kwargs,
        )
        new_values.append(
            value \
                if not isinstance(value, np.ndarray) \
                    else tf.convert_to_tensor(value)
        )
    values = new_values

    # TensorFlow does not support Concat for scalar values, so convert to tensor
    values = [
        value if len(value.shape) > 0 else tf.reshape(value, [1]) for value in values
    ]

    # Generation of TF OP
    try:
        # normal concat attempt
        tf_layers_dict[graph_node_output.name]['tf_node'] = \
            tf.concat(
                values=values,
                axis=axis,
                name=graph_node.name,
            )
    except:
        # Workaround to reduce error rate when merging tensors with undefined dimensions
        try:
            # Attempts to bind with the axis specified in ONNX
            tf_layers_dict[graph_node_output.name]['tf_node'] = \
                tf.concat(
                    values=values,
                    axis=int(graph_node.attrs.get('axis', 0)),
                    name=graph_node.name,
                )
        except:
            # If not successful with the same axis as ONNX, try to combine by other axes
            # Trial in reverse order from the axis at the end
            value_rank = len(values[0].shape)
            succeed = False
            for idx in reversed(range(value_rank)):
                try:
                    tf_layers_dict[graph_node_output.name]['tf_node'] = \
                        tf.concat(
                            values=values,
                            axis=idx,
                            name=graph_node.name,
                        )
                    succeed = True
                except:
                    pass
            if not succeed:
                raise

    # Attempts to force axis correction when the number of axes in the combined tensor do not exactly match.
    # However, if more than 2 patterns of correct answers exist, give up the correction.
    # This workaround is useful when automatic axis correction is practically difficult,
    # such as when all tensors to be combined originate from Transpose or Reshape.
    # https://github.com/PINTO0309/onnx2tf/issues/473
    output_tensor_shape = tf_layers_dict[graph_node_output.name]['tf_node'].shape
    if output_tensor_shape != tf.TensorShape(None):
        output_tensor_rank = len(output_tensor_shape)
        if graph_node.outputs[0].shape is not None \
            and axis != 0 \
            and output_tensor_rank >= 2 \
            and before_axis == axis:

            # Search for valid Concat patterns
            if not shape_is_equal_ignore_order(list(graph_node.outputs[0].shape), list(output_tensor_shape)):
                matched_axes = []
                for dummy_axis in range(1, output_tensor_rank):
                    try:
                        dummy_concat_tensor = \
                            tf.concat(
                                values=values,
                                axis=dummy_axis,
                                name=graph_node.name,
                            )
                        dummy_output_shape = dummy_concat_tensor.shape
                        if shape_is_equal_ignore_order(list(graph_node.outputs[0].shape), list(dummy_output_shape)):
                            matched_axes.append(dummy_axis)
                    except:
                        pass
                # Review Concat axes only if there is one valid join pattern
                if len(matched_axes) == 1:
                    tf_layers_dict[graph_node_output.name]['tf_node'] = \
                        tf.concat(
                            values=values,
                            axis=matched_axes[0],
                            name=graph_node.name,
                        )

    # Post-process transpose
    tf_layers_dict[graph_node_output.name]['tf_node'] = post_process_transpose(
        value_before_transpose=tf_layers_dict[graph_node_output.name]['tf_node'],
        param_target='outputs',
        param_name=graph_node.outputs[0].name,
        **kwargs,
    )

    # Generation of Debug Info
    tf_inputs = {f"input{idx}": value for idx, value in enumerate(values)}
    tf_inputs['axis'] = axis
    tf_layers_dict[graph_node_output.name]['tf_node_info'] = \
        make_tf_node_info(
            node_info={
                'tf_op_type': tf.concat,
                'tf_inputs': tf_inputs,
                'tf_outputs': {
                    'output': tf_layers_dict[graph_node_output.name]['tf_node'],
                },
            }
        )
