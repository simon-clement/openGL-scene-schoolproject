from src.transform import lerp, vec, quaternion_slerp, quaternion_matrix, quaternion, quaternion_from_euler, translate, scale
from bisect import bisect_left      # search sorted keyframe lists


class TransformKeyFrames:
    """ KeyFrames-like object dedicated to 3D transforms """
    def __init__(self, translate_keys, rotate_keys, scale_keys):
        """ stores 3 keyframe sets for translation, rotation, scale"""
        self.kf_translate = KeyFrames(translate_keys, lerp);
        self.kf_rotate = KeyFrames(rotate_keys, quaternion_slerp);
        self.kf_scale = KeyFrames(scale_keys, lerp);

    def value(self, time):
        """Compute each component's interpolation and compose TRS matrix"""
        val_tr = self.kf_translate.value(time)
        val_rot = self.kf_rotate.value(time)
        val_scale = self.kf_scale.value(time)
        return translate(val_tr) @ \
                quaternion_matrix(val_rot) @ \
                scale(val_scale)


class KeyFrames:
    """ Stores keyframe pairs for any value type with interpolation_function"""
    def __init__(self, time_value_pairs, interpolation_function=lerp):
        if isinstance(time_value_pairs, dict):  # convert to list of pairs
            time_value_pairs = time_value_pairs.items()
            keyframes = sorted(((key[0], key[1]) for key in time_value_pairs))
            self.times, self.values = zip(*keyframes)  # pairs list -> 2 lists
            self.interpolate = interpolation_function
        else:
            raise  # on fait rien si on nous envoie pas un dict

    def value(self, time):
        """ Computes interpolated value from keyframes, for a given time """

        # 1. ensure time is within bounds else return boundary keyframe
        if time <= self.times[0]:
            return self.values[0]
        if time >= self.times[-1]:
            return self.values[-1]
        # 2. search for closest index entry in self.times, using bisect_left function
        i = bisect_left(self.times, time) - 1
        # 3. using the retrieved index, interpolate between the two neighboring values
        # in self.values, using the initially stored self.interpolate function
        fraction = (time - self.times[i]) \
                / (self.times[i+1] - self.times[i])
        return self.interpolate(self.values[i], 
                self.values[i+1], fraction)
