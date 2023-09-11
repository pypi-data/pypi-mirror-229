use std::ops::Deref;

const MASKS_2D: [u64; 6] = [
    0x00000000FFFFFFFF,
    0x0000FFFF0000FFFF,
    0x00FF00FF00FF00FF,
    0x0F0F0F0F0F0F0F0F,
    0x3333333333333333,
    0x5555555555555555,
];
const MASKS_3D: [u64; 6] = [
    0x1fffff,
    0x1f00000000ffff,
    0x1f0000ff0000ff,
    0x100f00f00f00f00f,
    0x10c30c30c30c30c3,
    0x1249249249249249,
];

fn first_set_bit(value: u64) -> u32 {
    let mut mask = 1u64 << 63;
    for i in 0..64 {
        if value & mask > 0 {
            return i;
        }
        mask >>= 1;
    }
    64
}

fn bloat<const D: usize>(value: u32) -> u64 {
    let mut v = value as u64;

    match D {
        2 => {
            let m = &MASKS_2D;
            v = (v | v << 32) & m[0];
            v = (v | v << 16) & m[1];
            v = (v | v << 8) & m[2];
            v = (v | v << 4) & m[3];
            v = (v | v << 2) & m[4];
            v = (v | v << 1) & m[5];
        }
        3 => {
            let m = &MASKS_3D;
            v &= m[0];
            v = (v | v << 32) & m[1];
            v = (v | v << 16) & m[2];
            v = (v | v << 8) & m[3];
            v = (v | v << 4) & m[4];
            v = (v | v << 2) & m[5];
        }
        _ => panic!(
            "Morton number encoding of {}-dimensional points is not supported",
            D
        ),
    }

    v
}

fn shrink<const D: usize>(mut v: u64) -> u32 {
    match D {
        2 => {
            let m = &MASKS_2D;
            v &= m[5];
            v = (v ^ (v >> 1)) & m[4];
            v = (v ^ (v >> 2)) & m[3];
            v = (v ^ (v >> 4)) & m[2];
            v = (v ^ (v >> 8)) & m[1];
            v = (v ^ (v >> 16)) & m[0];
        }
        3 => {
            let m = &MASKS_3D;
            v &= m[5];
            v = (v ^ (v >> 2)) & m[4];
            v = (v ^ (v >> 4)) & m[3];
            v = (v ^ (v >> 8)) & m[2];
            v = (v ^ (v >> 16)) & m[1];
            v = (v ^ (v >> 32)) & m[0];
        }
        _ => panic!(
            "Morton number dencoding of {}-dimensional points is not supported",
            D
        ),
    }

    v as u32
}

fn encode<const D: usize>(point: &[u32; D]) -> u64 {
    (0..D)
        .map(|d| bloat::<D>(point[d] as u32) << d)
        .fold(0, |value, v| value | v)
}

fn decode<const D: usize>(code: u64, point: &mut [u32; D]) {
    for (i, x) in point.iter_mut().enumerate() {
        *x = shrink::<D>(code >> i);
    }
}

#[derive(Default, Clone, Copy, Debug)]
pub struct MortonCode<const D: usize>(u64);

impl<const D: usize> Deref for MortonCode<D> {
    type Target = u64;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<const D: usize> From<u64> for MortonCode<D> {
    fn from(value: u64) -> Self {
        Self(value)
    }
}

impl<const D: usize> MortonCode<D> {
    pub fn encode(point: &[u32; D]) -> Self {
        Self(encode(point))
    }

    #[allow(unused)]
    pub fn decode(&self, point: &mut [u32; D]) {
        decode(self.0, point);
    }

    pub fn decode_at_level(&self, level: u32, point: &mut [u32; D]) {
        let mut v = self.0;
        let offset = D as u32 * level;
        v >>= offset;
        v <<= offset;
        decode(v, point);
    }

    pub fn parent_level(&self, other: &MortonCode<D>) -> u32 {
        (64.0 / D as f32 - first_set_bit(self.0 ^ other.0) as f32 / D as f32).ceil() as u32
    }
}
