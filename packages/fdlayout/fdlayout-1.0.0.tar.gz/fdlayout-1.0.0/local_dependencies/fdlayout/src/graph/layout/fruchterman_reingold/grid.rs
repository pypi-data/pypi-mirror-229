use std::{collections::HashMap, ops::AddAssign};

use nalgebra::SVector;

pub type Point<const D: usize> = SVector<f32, D>;

#[derive(Default)]
pub struct Grid<const D: usize> {
    origin: Option<Point<D>>,
    cell_size: f32,
    cells: HashMap<[u32; D], Vec<usize>>,
}

impl<const D: usize> Grid<D> {
    fn point_to_key(&self, point: &Point<D>) -> [u32; D] {
        let rp = (point - self.origin.unwrap()) / self.cell_size;
        let mut key = [0u32; D];
        for d in 0..D {
            key[d] = rp[d] as u32;
        }
        key
    }

    pub fn build(&mut self, particles: &[Point<D>], cell_size: f32) {
        assert!(D >= 2);

        self.cell_size = cell_size;
        self.cells.clear();

        let mut origin = Point::zeros();
        for d in 0..D {
            let mut val = f32::MAX;
            for p in particles {
                val = val.min(p[d]);
            }
            origin[d] = val;
        }
        self.origin = Some(origin);

        for (i, p) in particles.iter().enumerate() {
            let key = self.point_to_key(p);

            match self.cells.get_mut(&key) {
                Some(cell) => {
                    cell.push(i);
                }
                None => {
                    self.cells.insert(key, vec![i]);
                }
            }
        }
    }

    pub fn query_sum<T: AddAssign, K: FnMut(usize) -> Option<T>>(
        &self,
        mut init: T,
        particle: &Point<D>,
        mut kernel: K,
    ) -> T {
        let key = self.point_to_key(particle);

        macro_rules! evaluate_cell {
            ($key:expr) => {
                if let Some(cell) = self.cells.get(&$key) {
                    for p in cell {
                        if let Some(value) = kernel(*p) {
                            init += value;
                        }
                    }
                }
            };
        }

        if D < 4 {
            for i in -1..=1 {
                let x = key[0] as i32 + i;
                if x >= 0 {
                    for j in -1..=1 {
                        let y = key[1] as i32 + j;
                        if y >= 0 {
                            let mut l = key.clone();
                            l[0] = x as u32;
                            l[1] = y as u32;
                            if D == 3 {
                                for k in -1..=1 {
                                    let z = key[2] as i32 + k;
                                    if z >= 0 {
                                        l[2] = z as u32;
                                        evaluate_cell!(l);
                                    }
                                }
                            } else {
                                evaluate_cell!(l);
                            }
                        }
                    }
                }
            }
        } else {
            evaluate_cell!(key);

            for d in 0..D {
                let i = key[d];
                for j in 0..2 {
                    let k = i as i32 + 2 * j - 1;
                    if k >= 0 {
                        let mut other_key = key.clone();
                        other_key[d] = k as u32;
                        evaluate_cell!(other_key);
                    }
                }
            }

            'outer: for i in 0..(2u32.pow(D as u32)) {
                let mut other_key = key.clone();
                for d in 0..D {
                    let k = key[d] as i32 + if i & (1u32 << d) > 0 { -1 } else { 1 };
                    if k < 0 {
                        continue 'outer;
                    }
                    other_key[d] = k as u32;
                }
                evaluate_cell!(other_key);
            }
        }

        init
    }

    pub fn cell_size(&self) -> f32 {
        self.cell_size
    }

    pub fn forall_cell_centers<F: FnMut(Point<D>)>(&self, mut kernel: F) {
        for k in self.cells.keys() {
            let mut p = Point::<D>::zeros();
            for d in 0..D {
                p[d] = (k[d] as f32 + 0.5) * self.cell_size;
            }
            kernel(p + self.origin.unwrap());
        }
    }

    pub fn n_cells(&self) -> usize {
        self.cells.len()
    }
}
