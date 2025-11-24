package nationalparktsp;

import org.cicirello.permutations.Permutation;
import org.cicirello.search.Configurator;
import org.cicirello.search.SolutionCostPair;
import org.cicirello.search.evo.AdaptiveEvolutionaryAlgorithm;
import org.cicirello.search.evo.FitnessProportionalSelection;
import org.cicirello.search.evo.InverseCostFitnessFunction;
import org.cicirello.search.operators.permutations.EnhancedEdgeRecombination;
import org.cicirello.search.operators.permutations.PermutationInitializer;
import org.cicirello.search.operators.permutations.ReversalMutation;
import org.cicirello.search.problems.tsp.RandomTSPMatrix;

import com.opencsv.CSVReader;
import com.opencsv.exceptions.CsvValidationException;

import java.io.FileReader;
import java.io.IOException;

public final class TSPAdaptiveEvolutionaryAlgorithm {

    // Container for both distance matrix and park names
    public static class TSPData {
        public final double[][] matrix;
        public final String[] names;

        public TSPData(double[][] matrix, String[] names) {
            this.matrix = matrix;
            this.names = names;
        }
    }

    public static void main(String[] args) throws IOException, CsvValidationException {

        Configurator.configureRandomGenerator(101);

        // Load matrix + park names from CSV file
        String filename = "DataScraping\\drivableDistanceMatrix.csv";
        TSPData data = loadMatrix(filename);

        double[][] distanceMatrix = data.matrix;
        String[] parkNames = data.names;

        int numCities = 51;

        RandomTSPMatrix.Double problem = new RandomTSPMatrix.Double(distanceMatrix);

        int populationSize = 100;
        int maxGenerations = 1000;
        int numElite = 10;

        // Run adaptive evolutionary algorithm
        AdaptiveEvolutionaryAlgorithm<Permutation> aea =
            new AdaptiveEvolutionaryAlgorithm<Permutation>(
                populationSize,
                new ReversalMutation(),
                new EnhancedEdgeRecombination(),
                new PermutationInitializer(numCities),
                new InverseCostFitnessFunction<Permutation>(problem),
                new FitnessProportionalSelection(),
                numElite);

        SolutionCostPair<Permutation> solution = aea.optimize(maxGenerations);

        System.out.println("Best tour length: " + solution.getCost());

        // Convert permutation to park names
        Permutation perm = solution.getSolution();
        StringBuilder sb = new StringBuilder();
        sb.append("Route: [");

        for (int i = 0; i < perm.length(); i++) {
            int idx = perm.get(i);
            sb.append(parkNames[idx]);
            if (i < perm.length() - 1) sb.append(", ");
        }

        sb.append("]");

        System.out.println(sb.toString());
    }

    private static TSPData loadMatrix(String filename) throws IOException, CsvValidationException {
        int size = 51;
        double[][] matrix = new double[size][size];
        String[] names = new String[size];

        // Read CSV
        try (CSVReader reader = new CSVReader(new FileReader(filename))) {
            String[] row;
            reader.readNext(); // skip header row
            int i = 0;

            while ((row = reader.readNext()) != null && i < size) {
                names[i] = row[0]; // First column = park name

                for (int j = 0; j < size; j++) {
                    matrix[i][j] = Math.round(
                        Double.parseDouble(row[j + 1]) * 10000.0
                    ) / 10000.0;
                }

                i++;
            }
        }

        return new TSPData(matrix, names);
    }
}